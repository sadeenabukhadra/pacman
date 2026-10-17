        screen_manager.register(
            "high_scores", lambda: HighScoresScreen(surface, change),
        )
        screen_manager.register("settings", lambda: settings_screen)

        def show_game_over(score: int) -> None:
            """Keep the completed score before creating its result screen."""
            nonlocal final_score
            final_score = score
            change("game_over")

        screen_manager.register(
            "game_over",
            lambda: GameOverScreen(
                surface=surface,
                change_screen=change,
                score=final_score,
            ),
        )

        def create_gameplay_screen() -> GameplayScreen:
            """Create a fresh run each time Play Again is selected."""
            return GameplayScreen(
                surface=surface,
                maze=create_first_maze(),
                theme_manager=theme_manager,
                asset_manager=asset_manager,
                on_game_over=show_game_over,
                lives=STARTING_LIVES,
                level_max_time=LEVEL_MAX_TIME,
            )

        screen_manager.register("gameplay", create_gameplay_screen)
        change("menu")
        running = True
        while running:
            dt = clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_F11):
                    pygame.display.toggle_fullscreen()
                    continue
                if screen_manager.current_screen is not None:
                    screen_manager.current_screen.handle_event(event)
            if not running:
                break
            if screen_manager.current_screen is not None:
                screen_manager.current_screen.update(dt)
            if screen_manager.current_screen is not None:
                screen_manager.current_screen.render()
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
