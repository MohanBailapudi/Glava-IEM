import math

def batter_degradaion_cost(soc, discharge_current):
    v_nom = 350
    c_rated = 35000
    dod_r = 80
    l_r = 1500
    replacement_cost = 3000
    v_full = 370
    q_nom = 80
    q_exp = 10
    q = 100
    v_exp = 360
    A = v_full - v_exp
    B = 3 / q_exp
    R = 1
    v_r = 350
    k = (v_full - v_nom + A * (math.exp(-B * q_nom)) * (q - q_nom)) / q_nom
    cost = c_rated * dod_r * (0.9 * l_r - 0.1)
    alpha = (R + k /(soc/100))/v_r**2
    beta = (c_rated*k*(1-(soc/100)))/(v_r**2*(soc/100))
    p_loss = alpha*(discharge_current*350)**2 + beta*(discharge_current*350)
    c_bat = replacement_cost/cost
    p_d = discharge_current*350
    f_bat = c_bat*(p_d - p_loss)*100
    return f_bat