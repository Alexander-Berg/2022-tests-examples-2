from sandbox.projects.yappy.configs import main_configs


GoodsRuntimeTestConfig = main_configs.BetaTemplateConfig(
    template_name='goods-runtime-test',
    components=[
        main_configs.BetaTemplateComponentConfig(
            id='goods-runtime',
            patch=main_configs.PatchConfig(
                parent_external_id='goods-runtime-yappy-template',
                resources=[
                    main_configs.ResourceConfig(
                        local_path='goods-runtime-backend.tar.gz',
                    ),
                ]
            )
        )
    ]
)
