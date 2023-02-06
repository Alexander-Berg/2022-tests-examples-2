
import logging
import re

TEXT_CELL_WIDTH = 35000


def get_object_info_url(object_id):
    return 'http://acab.search.yandex.net:8001/?text=%23{}'.format(object_id)


def get_hypo_color(hypo):
    COLORS_BY_CLASS = {
        True: 0x11,  # Green
        False: 0x2  # Red
    }

    return COLORS_BY_CLASS[hypo.is_false_positive()]


class StyleHolder:
    GOOD_COLORS = [0x2, 0x4, 0x6, 0x10, 0x14, 0x13, 0x12, 0x17, 0x11, 0x3, 0x18, 0x35, 0x30, 0x34, 0x3e]

    def __init__(self):
        self.colors = StyleHolder.GOOD_COLORS[:]
        self.cur_color_index = 0
        self.object_styles = dict()

    def get_style(self, color, underline=False):
        if color is None:
            color_index = self.cur_color_index
            self.cur_color_index = (self.cur_color_index + 1) % len(self.colors)
        else:
            if color not in self.colors:
                self.colors.append(color)
            color_index = self.colors.index(color)

        if (color_index, underline) not in self.object_styles:
            import xlwt
            fnt = xlwt.Font()
            fnt.name = 'Arial'
            fnt.colour_index = StyleHolder.GOOD_COLORS[color_index]
            fnt.bold = True
            fnt.Size = 12
            fnt.underline = underline

            style = xlwt.XFStyle()
            style.font = fnt
            style.alignment.vert = xlwt.Alignment.VERT_TOP
            style.alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
            style.alignment.shri = xlwt.Alignment.SHRINK_TO_FIT
            self.object_styles[(color_index, underline)] = style

        return self.object_styles[(color_index, underline)]


class RichTextBuilder:
    def __init__(self):
        self.style_holder = StyleHolder()

    def build_rich_text(self, source_text, hypos):
        rich_text = []
        cur_pos = 0

        for hypo in sorted(hypos, key=lambda k: k.begin):
            # TODO: Drow intersections in hypos
            # assert(hypo.begin >= cur_pos)

            filtered_text = re.sub('\\t', ' ', source_text[cur_pos: hypo.begin])
            filtered_text = re.sub(' \\n', '\n', filtered_text)
            filtered_text = re.sub('[\t ]+', ' ', filtered_text)
            filtered_text = re.sub('\n+', '\n', filtered_text)
            rich_text.append(filtered_text)

            font = self.style_holder.get_style(get_hypo_color(hypo)).font
            rich_text.append((source_text[hypo.begin: hypo.end], font))
            cur_pos = hypo.end

        rich_text.append(source_text[cur_pos:])

        return rich_text


def calc_row_height(text, cell_width):
    '''Try to autofit Arial 12'''
    row_count = sum([len(line) * 290 / cell_width + 1 for line in text.split('\n')])

    return 260 * row_count


class MarkupViewCreator:
    def __init__(self):
        logging.info('Installing xlwt...')

        self.rich_text_builder = RichTextBuilder()

    def create(self, markup_errors, texts_path, output):
        import xlwt
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet('markup', True)

        NUM_COL_INDEX = 0
        TEXT_ID_COL_INDEX = 1
        TEXT_COL_INDEX = 2
        OBJECTS_COL_INDEX = 3

        sheet.col(NUM_COL_INDEX).width = 2000
        sheet.col(TEXT_ID_COL_INDEX).width = 2000
        sheet.col(TEXT_COL_INDEX).width = TEXT_CELL_WIDTH
        sheet.col(OBJECTS_COL_INDEX).width = 15000

        table_row_index = 1
        text_index = 0

        alignment = xlwt.Alignment()
        alignment.vert = xlwt.Alignment.VERT_TOP
        alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
        alignment.shri = xlwt.Alignment.SHRINK_TO_FIT

        cell_style = xlwt.XFStyle()
        cell_style.alignment = alignment
        cell_style.font.bold = False
        cell_style.font.Size = 12

        with open(texts_path, 'r') as texts:
            for line in texts:
                text_id, text = line.strip().split('\t', 1)
                text_id = int(text_id)
                # Pool texts format
                text.replace('\t', '\n')
                text = text.decode('utf-8')

                hypos = markup_errors[text_id]
                if not hypos:
                    continue

                rich_text = self.rich_text_builder.build_rich_text(text, hypos)

                sheet.write(table_row_index, NUM_COL_INDEX, str(text_index), cell_style)
                sheet.write(table_row_index, TEXT_ID_COL_INDEX, str(text_id), cell_style)
                sheet.write_rich_text(table_row_index, TEXT_COL_INDEX, rich_text, cell_style)

                # Write object info urls
                object_info_ids = set()
                for hypo in hypos:
                    if (hypo.object_id, hypo.is_false_positive()) in object_info_ids:
                        continue

                    # hypo_text = text[hypo.begin:hypo.end]
                    sheet.write(table_row_index + len(object_info_ids),
                                OBJECTS_COL_INDEX,
                                xlwt.Formula('HYPERLINK("{}", "{} (#{})")'.format(get_object_info_url(hypo.object_id), hypo.object_id, hypo.object_id)),
                                self.rich_text_builder.style_holder.get_style(get_hypo_color(hypo), underline=True))
                    object_info_ids.add((hypo.object_id, hypo.is_false_positive()))

                # Shrink to fit cell heights
                sheet.merge(table_row_index, table_row_index + len(object_info_ids), NUM_COL_INDEX, NUM_COL_INDEX)
                sheet.merge(table_row_index, table_row_index + len(object_info_ids), TEXT_ID_COL_INDEX, TEXT_ID_COL_INDEX)
                sheet.merge(table_row_index, table_row_index + len(object_info_ids), TEXT_COL_INDEX, TEXT_COL_INDEX)

                text_cell_height = calc_row_height(text, TEXT_CELL_WIDTH)
                last_object_cell_height = text_cell_height - len(object_info_ids) * 20
                sheet.row(table_row_index + len(object_info_ids)).height = int(last_object_cell_height)

                table_row_index += len(object_info_ids) + 2
                text_index += 1

        book.save(output)
