import torch
import argparse

from utils.init_env import init_env
from utils.utils import create_log_dir
from algorithms.policy_gradient import AgentInference
from algorithms.ppo import PPO
from trainers.on_policy import OnPolicyTrainer


def main(args):
    observation_size, action_size, image_env = create_log_dir(args)

    # init env
    train_env = init_env(
        args.env_name, args.train_env_num,
        action_repeat=args.action_repeat,
        die_penalty=args.die_penalty,
        max_len=args.max_episode_len
    )
    test_env = init_env(args.env_name, args.test_env_num, action_repeat=args.action_repeat)

    # init agent
    device_online = torch.device(args.device_online)
    device_train = torch.device(args.device_train)

    agent_online = AgentInference(
        image_env,
        observation_size, action_size, args.hidden_size, device_online,
        args.policy
    )

    agent_train = PPO(
        image_env,
        observation_size, action_size, args.hidden_size, device_train,
        args.policy, args.normalize_adv, args.returns_estimator,
        args.learning_rate, args.gamma, args.entropy, args.clip_grad,
        image_augmentation_alpha=args.image_aug_alpha,
        gae_lambda=args.gae_lambda,
        ppo_epsilon=args.ppo_epsilon,
        use_ppo_value_loss=args.ppo_value_loss,
        rollback_alpha=args.rollback_alpha,
        recompute_advantage=args.recompute_advantage,
        ppo_n_epoch=args.ppo_n_epoch,
        ppo_n_mini_batches=args.ppo_n_mini_batches,
    )

    # init and run trainer
    trainer = OnPolicyTrainer(
        agent_online, agent_train, args.update_period, False,
        train_env, test_env,
        args.normalize_obs, args.normalize_reward,
        args.obs_clip, args.reward_clip,
        args.log_dir
    )
    if args.load_checkpoint is not None:
        trainer.load(args.load_checkpoint)
    trainer.train(args.n_epoch, args.n_step_per_epoch, args.rollout_len, args.n_tests_per_epoch)

    train_env.close()
    test_env.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_dir", type=str)
    parser.add_argument("--load_checkpoint", type=str)

    # env
    parser.add_argument("--env_name", type=str)
    parser.add_argument("--action_repeat", type=int)
    parser.add_argument("--die_penalty", type=int, default=0)
    parser.add_argument("--max_episode_len", type=int, default=0)
    parser.add_argument("--train_env_num", type=int)
    parser.add_argument("--test_env_num", type=int)

    # nn
    parser.add_argument("--hidden_size", type=int)
    parser.add_argument("--device_online", type=str)
    parser.add_argument("--device_train", type=str)
    parser.add_argument("--image_aug_alpha", type=float, default=0.0)

    # policy & advantage
    parser.add_argument("--policy", type=str)
    parser.add_argument("--normalize_adv", action='store_true')
    parser.add_argument("--returns_estimator", type=str, default='gae')

    # optimization
    parser.add_argument("--learning_rate", type=float, default=0.0003)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--entropy", type=float, default=1e-3)
    parser.add_argument("--clip_grad", type=float, default=0.5)
    parser.add_argument("--gae_lambda", type=float, default=0.9)

    # ppo
    parser.add_argument("--ppo_epsilon", type=float, default=0.2)
    parser.add_argument("--ppo_value_loss", action='store_true')
    parser.add_argument("--rollback_alpha", type=float, default=0.0)
    parser.add_argument("--recompute_advantage", action='store_true')
    parser.add_argument("--ppo_n_epoch", type=int)
    parser.add_argument("--ppo_n_mini_batches", type=int)

    # trainer
    parser.add_argument("--normalize_obs", action='store_true')
    parser.add_argument("--normalize_reward", action='store_true')
    parser.add_argument("--obs_clip", type=float, default=-float('inf'))
    parser.add_argument("--reward_clip", type=float, default=float('inf'))
    parser.add_argument("--update_period", type=int, default=1)

    # training
    parser.add_argument("--n_epoch", type=int)
    parser.add_argument("--n_step_per_epoch", type=int)
    parser.add_argument("--rollout_len", type=int)
    parser.add_argument("--n_tests_per_epoch", type=int)

    return parser.parse_args()


if __name__ == '__main__':
    args_ = parse_args()
    main(args_)
