import xlwings as xw
from math import log, sqrt, exp
from scipy.stats import norm
from scipy.optimize import bisect
import QuantLib as ql


@xw.func
def black_scholes(today, expiry, discount_factor, forward, parity, strike, vol):
    ttm = (expiry - today).days / 365
    dp = 1.0 / (vol * sqrt(ttm)) * (log(forward / strike) + 0.5 * vol ** 2 * ttm)
    dm = 1.0 / (vol * sqrt(ttm)) * (log(forward / strike) - 0.5 * vol ** 2 * ttm)
    return discount_factor * parity * (forward * norm.cdf(parity * dp) - strike * norm.cdf(parity * dm))


@xw.func
@xw.arg('parity', ndim=1)
@xw.arg('strike', ndim=1)
@xw.arg('premium', ndim=1)
@xw.ret(transpose=True)
def imp_vol(today, expiry, underlying, riskfree, dividend_yield, parity, strike, premium):
    ttm = (expiry - today).days / 365
    forward = underlying * exp((riskfree - dividend_yield) * ttm)
    discount_factor = exp(-riskfree * ttm)
    res = []
    for i in range(len(parity)):
        vol = bisect(
            lambda vol: premium[i] - black_scholes(
                today,
                expiry,
                discount_factor,
                forward,
                parity[i],
                strike[i],
                vol
            ),
            0.0000001,
            100.0
        )
        res.append(vol)
    return res


@xw.func
@xw.arg('parity', ndim=1)
@xw.arg('strike', ndim=1)
@xw.arg('premium', ndim=1)
@xw.ret(transpose=True)
def imp_vol_ql(today, settlement, expiry, underlying, riskfree, dividend_yield, parity, strike, premium):
    # Dates
    today = ql.Date(today.day, today.month, today.year)
    settlement = ql.Date(settlement.day, settlement.month, settlement.year)
    expiry = ql.Date(expiry.day, expiry.month, expiry.year)
    ql.Settings.instance().evaluationDate = today

    # Market data
    underlying = ql.SimpleQuote(underlying)
    r = ql.SimpleQuote(riskfree)  # risk-free rate
    q = ql.SimpleQuote(dividend_yield)  # dividend yield 0.016
    vol = ql.SimpleQuote(0.20)  # only needed for price process, not relevant for implied vol
    dcc = ql.Actual365Fixed()

    risk_free_curve = ql.FlatForward(settlement, ql.QuoteHandle(r), dcc)
    div_yield_curve = ql.FlatForward(settlement, ql.QuoteHandle(q), dcc)
    vol_curve = ql.BlackConstantVol(today, ql.UnitedStates(ql.UnitedStates.NYSE), ql.QuoteHandle(vol), dcc)

    res = []
    for i in range(len(parity)):
        # Instantiating the option
        exercise = ql.AmericanExercise(settlement, expiry)
        if parity[i] == 1:
            type = ql.Option.Call
        elif parity[i] == -1:
            type = ql.Option.Put
        payoff = ql.PlainVanillaPayoff(type, strike[i])
        option = ql.VanillaOption(payoff, exercise)

        # Set up price process
        process = ql.BlackScholesMertonProcess(s0=ql.QuoteHandle(underlying),
                                               dividendTS=ql.YieldTermStructureHandle(div_yield_curve),
                                               riskFreeTS=ql.YieldTermStructureHandle(risk_free_curve),
                                               volTS=ql.BlackVolTermStructureHandle(vol_curve)
                                               )

        res.append(option.impliedVolatility(premium[i], process))
    return res

if __name__ == '__main__':
    xw.serve()
