from worlds.LauncherComponents import Component, Type, components, launch

from .data.game_info import GAME_NAME


def run_client(*args: str) -> None:
    # Import paresseux : le client n'est chargé qu'à son lancement.
    from .client.client import main

    launch(main, name="Pikmin 3 Beta Client", args=args)


components.append(
    Component(
        "Pikmin 3 Beta Client",
        func=run_client,
        game_name=GAME_NAME,
        component_type=Type.CLIENT,
        supports_uri=True,
    )
)
