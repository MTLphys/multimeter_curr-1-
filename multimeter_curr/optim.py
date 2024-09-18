import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import math

# Constants
lambda_ = 818 * 10**-9  # wavelength in meters
c = 3 * 10**8  # speed of light in m/s
del_lambda = 4 * 10**-9  # change in wavelength in meters
del_t = (0.314 * lambda_**2) / (c * del_lambda)  # time interval
k = (2 * math.pi) / lambda_  # wave number
L = 3 * 10**-6  # sample thickness in meters
alpha = 0.002315 * 2 * k  # absorption coefficient
Leff = (1 - math.exp(-alpha * L)) / alpha  # effective length
w0 = 4.6 * 10**-6  # beam waist in meters
i0 = ((11.165 * 10**-3) / ((80 * 10**6) / 20)) / (0.5 * math.pi * w0**2 * del_t)  # intensity
z0 = (k * w0**2) / 2  # raleigh range
print(i0*1e-14)

# Define the model function to compute transmittance
def transmittance_model(z, beta, x0,a):
    q0 = (beta * i0 * Leff) / (1 + (z-x0)**2 / z0**2)

    transmittance = np.zeros_like(q0)
    for i, q in enumerate(q0):
        t_sum = 0
        for m in range(201):  # including m=200
            term = (-q**m) / ((m + 1)**(3/2))
            if np.isfinite(term):
                t_sum += term
            else:
                #print("non finite at i,m =",i,m)
                t_sum += 0  # Ignore non-finite terms
        transmittance[i] = t_sum
    return a*transmittance

# Generate sample data
end = 10/1000  # end position
steps = 500  # number of steps
x0 = 5.5/1000 # position of the zero 
z = np.linspace(z0, end, steps)  # z values

# Use a true value for beta to generate noisy data
true_beta = 9.4e-13
truea = .87
q0 = (true_beta* i0 * Leff) / (1 + (z-x0)**2 / z0**2)
true_transmittance =transmittance_model(z, true_beta,x0,truea)
noise = np.random.normal(0, 0.00001, size=true_transmittance.shape)  # Add some noise
noisy_transmittance = true_transmittance + noise

# # Ensure there are no infs or NaNs in the noisy data
# if not np.all(np.isfinite(noisy_transmittance)):
#     raise ValueError("Noisy transmittance data contains infs or NaNs")
xg = 5.0/1000
ag= .95
betag =9e-13 
# # Fit the model to the noisy data
popt, pcov = curve_fit(transmittance_model, z, noisy_transmittance, p0=[betag,xg,ag])
fitted_beta = popt[0]
fitted_x0 = popt[1]
fitted_a = popt[2]
# Print the fitted beta value
print(f"Fitted beta: {fitted_beta}")
print(f"Fitted x0: {fitted_x0}")

# # Plot the results
plt.figure(figsize=(10, 6))
#plt.plot(z,q0,label='q0')
plt.plot(z, noisy_transmittance, 'b.', label='Noisy Data')
plt.plot(z, true_transmittance, 'g-', label='True Transmittance')
plt.plot(z, transmittance_model(z, fitted_beta,fitted_x0,fitted_a), 'r-', label=f'Fitted Model \n (beta={fitted_beta*1e13:.4f} 10^-13 ,x0={fitted_x0:.4f},a={fitted_a:.4f})')
plt.xlabel('z')
plt.ylabel('Transmittance')
plt.legend()
plt.show()

        