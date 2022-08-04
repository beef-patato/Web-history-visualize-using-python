# -*- coding : utf-8 -*-
# @Author : belli dura despicio
# @Time : 2022/8/2 16:01
# @File : analyse_data.py
# @software : PyCharm
# 针对EDGE的数据，制作不同页面访问次数的柱状图
import sqlite3
from pyecharts.charts import Bar
import re
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import os
import shutil


def get_data():
    if 'Web_data.db' not in os.listdir():
        default_path = os.path.expanduser("~") + r'\AppData\Local\Microsoft\Edge\User Data\Default\WebAssistDatabase'
        # different history files i think, but the history file is much more complex, not easy to interpret. So I choose
        # the WebAssistDatabase instead.
        #
        shutil.copy(default_path, './Web_data.db')  # 修改文件名防止错混
        print(f'copy and rename the data file in {default_path}.')
    else:
        print('Web_data.db already exists.')

    return 'Web_data.db'  # 返回数据库名


def analysis_data(dataBase, n):
    """
    处理数据，并且绘图
    :param dataBase: name of database
    :param n: user input the number want to be show in the html. -- top n
    :return:
    """
    dataBase = dataBase
    range_slice = slice
    if n == 'all':
        range_slice = slice(0, None)
    else:
        n = int(n)
        range_slice = slice(0, n)

    # 提取所有的域名
    conn = sqlite3.connect(dataBase)
    cur = conn.cursor()
    sql = """
    select url, num_visits from navigation_history;
    """
    links = cur.execute(sql)  # [(url1, count1), (), ...]
    links_need = [i for i in links]
    conn.commit()
    # 获取完整的访问过的域名,
    cur.close()
    conn.close()

    pattern = re.compile(r'(http[s]?://)([^/]+)')
    # 匹配较短的域名，统一站点下的不同页面统一格式
    sim_pairs = []
    for url, num in links_need:
        sim_url = pattern.findall(url)[0][1]
        temp = (sim_url, num)
        sim_pairs.append(temp)

    # 分类并且计数
    u_set = {i[0] for i in sim_pairs}  # 去重处理
    r_ls = []  # 存储结果
    for u in u_set:
        # 计数
        templs = []
        count = 0
        for j in sim_pairs:
            if j[0] == u:
                templs.append(j)
        for i in templs:
            count += i[1]
        r_ls.append((u, count))  # save as tuple in list [(url1, count1),(),...]
    r_ls.sort(key=lambda x: -x[1])  # sort the list by count number
    s_r_ls = r_ls[range_slice]
    # 默认前50, use the n

    uDic = dict(s_r_ls)
    # print(list(uDic.values()))
    # print(list(uDic.keys()))

    return uDic


def draw(uDic, n):
    uDic = uDic
    bar = (
        Bar(init_opts=opts.InitOpts(width="1500px",
                                    height="700px",
                                    page_title="my_history_webs",
                                    theme=ThemeType.LIGHT),)

        .add_xaxis(list(uDic.keys()))
        .add_yaxis(series_name='访问次数', y_axis=list(uDic.values()))
        .set_global_opts(title_opts=opts.TitleOpts(title=f"一段时间我的最常访问的网站, top_{n}", subtitle=f"这些共计{sum(uDic.values())}"),
                         yaxis_opts=opts.AxisOpts(axislabel_opts={'interval': '0'}),  # 显示所有的标签

                         )


        .reversal_axis()  # 翻转xy轴
        .set_series_opts(label_opts=opts.LabelOpts(position="right"))
        .render('my_history.html')
    )


if __name__ == '__main__':
    n = input('the number of most visited webs you want, \n'
              '"all" for all (better not), default is 50 (suggested), "q" for quit>>>')
    if n == 'q':
        pass
    else:
        if n == '':
            n = '50'
        dataBase = get_data()
        uDic = analysis_data(dataBase, n)
        draw(uDic, n)

    print('Thank you for using. :)')

