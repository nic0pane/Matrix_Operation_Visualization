import matplotlib.pyplot as plt
import numpy as np

def matrix_display(matrix):
    # Calcolo di autovalori e autovettori
    eigenvalues, eigenvectors = np.linalg.eig(matrix)

    fig, ax = plt.subplots()
    origin = [0, 0]

    # Disegna gli autovettori
    for i in range(len(matrix)):
        vec = eigenvectors[:, i]
        ax.quiver(
            *origin,
            vec[0],
            vec[1],
            angles='xy',
            scale_units='xy',
            scale=1,
            color=['r', 'b'][i],
            label=f'$\\lambda_{i+1} = {eigenvalues[i]:.2f}$'
        )
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.axhline(0, color='grey', lw=0.5)
    ax.axvline(0, color='grey', lw=0.5)
    plt.title(f'Eigenvectors of the Matrix {matrix}')
    plt.legend()
    plt.grid()
    plt.show()