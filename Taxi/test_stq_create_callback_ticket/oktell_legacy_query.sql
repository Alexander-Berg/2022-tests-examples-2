
            -- Проверяем line
            IF EXISTS (
                SELECT [id]
                FROM [oktell].[dbo].[_SPR_naim_support_kaluga_line]
                WHERE [Line] = %s
            )
            -- Если line есть в списке
            BEGIN
                -- Проверяем в открытых
                IF EXISTS (
                    SELECT [Ident]
                    FROM [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
                    WHERE [Number] = %s
                           -- Только открытых
                    and IsNull([Closed],0) = 0
                )
                  -- Если есть в открытых
                BEGIN
                    IF NOT EXISTS (
                        SELECT [Ident]
                        FROM [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
                        WHERE [Number] = %s
                        -- Только открытых
                        and IsNull([Closed],0) = 0
                        and [Line] = %s
                    )
                    -- Если line отличается, то
                    BEGIN
                        -- Сохраняем абонента
                        Insert Into
                            [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
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
                END -- IF EXISTS
                ELSE -- IF NOT EXISTS
                -- Если нет в открытых
                BEGIN
                    -- Сохраняем абонента
                    Insert Into
                        [oktell].[dbo].[_yandex_naim_support_kaluga_ext]
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
