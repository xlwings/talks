import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly
import plotly.graph_objs as go
import xlwings as xw

@xw.func
@xw.arg('x', pd.DataFrame)
def CORREL2(x):
    return x.corr()

@xw.func
@xw.arg('corr', pd.DataFrame)
def corr_plot(corr):
    wb = xw.Workbook.caller()
    ax = sns.heatmap(corr, vmin=-1, vmax=1, linewidths=.5)
    plt.yticks(rotation=0)
    plt.xticks(rotation=90)
    fig = ax.get_figure()
    xw.Plot(fig).show('CorrPlot', sheet=1)
    plt.close()
    return '<Corr Plot>'

@xw.func
@xw.arg('corr', pd.DataFrame)
def corr_plotly(corr):
    plotly.offline.plot({
        "data": [
            go.Heatmap(
                z=corr.iloc[::-1].values,
                x=list(corr.columns),
                y=list(reversed(corr.columns)),
                zmin=-1,
                zmax=1
            )
        ]
    })
    return '<Corr Plotly>'
