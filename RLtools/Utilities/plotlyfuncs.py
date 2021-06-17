#%%
import math
import plotly.graph_objects as go
def make_transparent(f):

    f.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)')
    return f


def draw_axes(f):
    kwargs = dict(showline=True, linecolor='gray')
    f.update_xaxes(**kwargs)
    f.update_yaxes(**kwargs)
    return f

def bottom_legend(f, **layoutkwargs):
    f.update_layout(legend = dict(xanchor='center', x=0.5, orientation= 'h', **layoutkwargs))
    return f


def add_sivers_watermark(f):
    f.update_layout(
        images=[dict(
            source="https://www.sivers-semiconductors.com/wp-content/themes/sivers/assets/img/logo_black.svg",
            sizex=0.8, sizey=0.8,
            x=0.5, y=0.5,
            xanchor="center", yanchor="middle",
            opacity=0.05
        )])
    return f



def tulip_template(f):
    """Template for plots used in the Tulip2 project. Has 1200x1200px, large text,
       transparent background with Sivers watermark, black axes (including secondary y)
       legend along the bottom of the figure.


    Args:
        f (go.Figure): the figure to modify

    Returns:
        [go.Figure]: the modified figure
    """    
    f.layout.width=1200
    f.layout.height=1200
    for func in [make_transparent, draw_axes, bottom_legend, add_sivers_watermark]:
        f=func(f)
    f.update_xaxes(showgrid=False)
    f.update_yaxes(showgrid=False)
    f.layout.font.size=28
    return f

#%%


class CalculateTicks:

    def __init__(self, data, tick_num):
        self.negative = False
        self.y_negative_ratio = None
        self.y_positive_ratio = None
        self.y_range_min = None
        self.y_range_max = None

        self.y_min = min(data)
        self.y_max = max(data)

        self.y_range = self.y_max - self.y_min if self.y_min < 0 else self.y_max
        self.y_range = self.y_range * 10000
        self.y_length = len(str(math.floor(self.y_range)))

        self.y_pw10_div = 10 ** (self.y_length - 1)
        self.y_first_digit = math.floor(self.y_range / self.y_pw10_div)
        self.y_max_base = self.y_pw10_div * self.y_first_digit / 10000

        self.y_dtick = self.y_max_base / tick_num
        self.y_dtick_ratio = self.y_range / self.y_dtick


def get_y_axis_dict(y_data, axis_names, tick_num, axis_colors, offset):

    """
    :param offset: the amount in ratio of figure size that the y axes should be offset
    :param axis_colors: a list of plotly colors
    :param tick_num: the number of ticks in the plot
    :param y_data: should be list like with each item being the y_data for plotting
    :param axis_names: the y_axis titles
    :return:
    """

    right_y_position = 1 - (len(y_data) - 1) * offset

    axis_class_list = []
    max_tick_ratio = 0
    for i, data in enumerate(y_data):
        tick_calculation = CalculateTicks(data, tick_num)
        axis_class_list.append(tick_calculation)
        max_tick_ratio = tick_calculation.y_dtick_ratio if tick_calculation.y_dtick_ratio > max_tick_ratio \
            else max_tick_ratio

    any_negative = False
    for i, tick_calculation in enumerate(axis_class_list):
        if tick_calculation.y_min < 0:
            any_negative = True
            axis_class_list[i].negative = True
            axis_class_list[i].y_negative_ratio = abs(
                tick_calculation.y_min / tick_calculation.y_range) * max_tick_ratio
        else:
            axis_class_list[i].y_negative_ratio = 0
        axis_class_list[i].y_positive_ratio = (tick_calculation.y_max / tick_calculation.y_range) * max_tick_ratio

    global_negative_ratio = 0
    global_positive_ratio = 0
    for i, tick_calculation in enumerate(axis_class_list):
        global_negative_ratio = tick_calculation.y_negative_ratio if tick_calculation.y_negative_ratio \
                                                                     > global_negative_ratio else global_negative_ratio
        global_positive_ratio = tick_calculation.y_positive_ratio if tick_calculation.y_positive_ratio \
                                                                     > global_positive_ratio else global_positive_ratio

    global_negative_ratio = global_negative_ratio + 0.1
    for i, tick_calculation in enumerate(axis_class_list):
        if any_negative:
            axis_class_list[i].y_range_min = global_negative_ratio * tick_calculation.y_dtick * -1
        else:
            axis_class_list[i].y_range_min = 0
        axis_class_list[i].y_range_max = global_positive_ratio * tick_calculation.y_dtick

    yaxis_dict = {}
    for i, data in enumerate(y_data):
        if i < 1:
            yaxis_dict = dict(yaxis=dict(
                title=axis_names[i],
                range=[axis_class_list[i].y_range_min, axis_class_list[i].y_range_max],
                dtick=axis_class_list[i].y_dtick,
                titlefont=dict(
                    color=axis_colors[i]
                ),
                tickfont=dict(
                    color=axis_colors[i]
                )
            )
            )

        else:
            y_axis_long = 'yaxis' + str(i + 2)
            yaxis_dict[y_axis_long] = dict(title=axis_names[i],
                                           range=[axis_class_list[i].y_range_min,
                                                  axis_class_list[i].y_range_max],
                                           dtick=axis_class_list[i].y_dtick,
                                           titlefont=dict(
                                               color=axis_colors[i]
                                           ),
                                           tickfont=dict(
                                               color=axis_colors[i]
                                           ),
                                           anchor="free" if i > 1 else 'x',
                                           overlaying="y",
                                           side="right",
                                           position=right_y_position + offset * (i-1))

    return yaxis_dict, right_y_position

