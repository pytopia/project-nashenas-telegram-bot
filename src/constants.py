from types import SimpleNamespace

import emoji

from src.utils.keyboard import create_keyboard

keys = SimpleNamespace(
    random_connect=emoji.emojize(':bust_in_silhouette: Random Connect'),
    settings=emoji.emojize(':gear: Settings'),
    exit=emoji.emojize(':cross_mark: Exit'),
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
