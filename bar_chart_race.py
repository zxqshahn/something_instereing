import pandas as pd
import numpy as np
from pyhive import hive
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.animation import FuncAnimation
from pylab import *
from IPython.display import HTML


# 供FuncAnimation调用
def init():
    ax.clear()
    nice_axes(ax)
    ax.set_ylim(.2, 6.8)


def update(i):
    for bar in ax.containers:
        bar.remove()
    y = df_rank_expanded.iloc[i]
    width = df_expanded.iloc[i]
    colors = plt.cm.Dark2(range(8))
    ax.barh(y=y, width=width, color=colors, tick_label=labels)


# 平滑处理逻辑
def prepare_data(df, steps=5):
    df = df.reset_index()
    df.index = df.index * steps
    last_idx = df.index[-1] + 1
    df_expanded = df.reindex(range(last_idx))
    df_expanded['c_day'] = df_expanded['c_day'].fillna(method='ffill')
    df_expanded = df_expanded.set_index('c_day')
    df_rank_expanded = df_expanded.rank(axis=1, method='first')
    df_expanded = df_expanded.interpolate()
    df_rank_expanded = df_rank_expanded.interpolate()
    labels = df_expanded.columns
    return df_expanded, df_rank_expanded, labels


if __name__ == '__main__':
    # 处理mpl中文字体问题
    mpl.rcParams["font.sans-serif"] = ["SimHei"]
    mpl.rcParams["axes.unicode_minus"] = False
    # 连接hive读数据并数据预处理
    conn = hive.Connection(host='127.0.0.1', port=10000, auth='CUSTOM', username='username', password='password')
    df = pd.read_sql(
        sql="SELECT c_day,team_name,ten_days_buy_amt FROM data_market.ads_team_controlrates_monitor_so where c_day < '2020-08-24'",
        con=conn)
    data_res = df.set_index(['c_day', 'team_name']).unstack().fillna(0).head(11)
    # 去除一级行索引
    data_res1 = data_res.droplevel(level=0, axis=1)
    # 挑选几只战队和适当时间比较
    data_res1 = data_res1[['178战队', '698战队', 'Avenger战队', '众志战队', '传奇战队', '先锋战队', '光芒战队', '凌霄战队', '利刃战队', '北斗战队']]
    data_res2 = data_res1.loc['2020-08-13':'2020-08-23']
    # 平滑过渡
    df_expanded, df_rank_expanded, labels = prepare_data(data_res2)
    # 动画
    fig = plt.Figure(figsize=(6, 3.5), dpi=144)
    ax = fig.add_subplot()
    anim = FuncAnimation(fig=fig, func=update, frames=len(df_expanded),
                         interval=200, repeat=False)
    # 展示
    html = anim.to_html5_video()
    HTML(html)