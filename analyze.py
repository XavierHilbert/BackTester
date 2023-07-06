import matplotlib.pyplot as plt
import seaborn as sns
import statistics
import math
import constants
from scipy import stats


def calc_confiendece_interval(net_amount: list):
    """Calculates t-confidence interval."""
    sample_standerd_deviation: float = statistics.stdev(net_amount)
    standerd_error: float = sample_standerd_deviation/math.sqrt(len(net_amount))
    margin_of_error: float = standerd_error * t_critical_value(len(net_amount) - 1, constants.SIGINFICANCE)
    mean: float = statistics.mean(net_amount)
    lower_bound: float = mean - margin_of_error
    upper_bound: float = mean + margin_of_error
    print(f"We are 99 confident that the bot can make between {lower_bound} percent and {upper_bound} precent.")


def t_critical_value(degrees_of_freedom: int, signficance_level: float):
    """Returns a t_cricital value for a two tailed test."""
    return (stats.t.ppf(1-signficance_level/2, degrees_of_freedom))


def graph(net_amount: list):
    """Graphs results. Plot a histogram and a normal distrubution on top of it."""
    sns.distplot(net_amount, hist=True, kde=True, 
             bins=int(180/5), color = 'darkblue', 
             hist_kws={'edgecolor':'black'},
             kde_kws={'linewidth': 4})
    plt.show()