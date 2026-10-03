from worlds.LauncherComponents import Component, Type, components, launch


def run_client(*args: str) -> None:
    # Import paresseux : le client n'est chargé qu'à son lancement.
    from .client.client import main

    launch(main, name="Pikmin 3 Client", args=args)


components.append(
    Component(
        "Pikmin 3 Client",
        func=run_client,
        game_name="Pikmin 3",
        component_type=Type.CLIENT,
        supports_uri=True,
    )
)
