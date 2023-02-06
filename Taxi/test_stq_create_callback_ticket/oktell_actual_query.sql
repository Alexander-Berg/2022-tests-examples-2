
        -- Проверяем line
        IF EXISTS (
            SELECT [id]
            FROM [oktell].[dbo].[_SPR_naim_support_kaluga_line]
            WHERE [Line] = %s
        )
        -- Если line есть в списке
        BEGIN
            IF EXISTS (
          SELECT [Ident]
            FROM [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
            WHERE [Number] = %s
            -- Только открытых
          and isnull([Closed],0) = 0
            )
            -- Если есть в открытых
            BEGIN
                IF NOT EXISTS (
                SELECT [Ident]
                FROM [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
                WHERE [Number] = %s
                and [Line] = %s
                -- Только открытых
              and isnull([Closed],0) = 0
                )
                -- Надо сохранять, line отличается
                BEGIN
              -- Надо сохранять, line отличается
                   Insert Into [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
                   ([DateAdd],[Number],[Fio],[Line],[Source], [RequestId])
                   values (
                        GetDate(),
                        %s,
                        %s,
                        %s,
                        'procedure',
                        %s
                    )
                END
          ELSE
            BEGIN
            --  Тикет в обработке?
            IF EXISTS (
                SELECT [Ident]
                FROM [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
                WHERE [Number] = @Number
                and [Line] = @Line
                -- Только открытых
                and isnull([Closed],0) = 0
            -- В обработе
              and IsNull([DialogScript],0) = 1
                )
                -- Надо сохранять, тикет в обработке
              BEGIN
                --Select 'Надо сохранять, тикет в обработке'
                -- Сохраняем абонента
                Insert Into [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
                ([DateAdd],[Number],[Fio],[Line],[Source], [RequestId])
                values (
                    GetDate(),
                    %s,
                    %s,
                    %s,
                    'procedure',
                    %s
                )
              END
            END
            END -- IF EXISTS
        ELSE -- IF NOT EXISTS
            -- Надо сохранять, абонента нет в открытых
            BEGIN
            --Select 'Надо сохранять, абонента нет в открытых'
                -- Сохраняем абонента
                Insert Into [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
                ([DateAdd],[Number],[Fio],[Line],[Source], [RequestId])
                values (
                    GetDate(),
                    %s,
                    %s,
                    %s,
                    'procedure',
                    %s
                )
            END
        END
