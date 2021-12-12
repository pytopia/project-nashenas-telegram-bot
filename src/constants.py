from types import SimpleNamespace

from src.utils.keyboard import create_keyboard
from loguru import logger

logger.info('Reading keyboards and keys...')
keys = SimpleNamespace(
    random_connect=':bust_in_silhouette: Random Connect',
    settings=':gear: Settings',
    exit=':cross_mark: Exit',
)

keyboards = SimpleNamespace(
    exit=create_keyboard(keys.exit),
    main=create_keyboard(keys.random_connect, keys.settings),
)

states = SimpleNamespace(
    random_connect='RANDOM_CONNECT',
    main='MAIN',
    connected='CONNECTED',
)
