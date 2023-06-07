#Development of final plots and results potentially to be incorporated in Main.py.

import matplotlib.pyplot as plt


#Weight Evolution Plots
def SimpleWeightsPlot(max_iter, w_evolve):
        
    iterations = list(range(1, max_iter+1))
            
    first_values = [subarray[0] for subarray in w_evolve]
    second_values = [subarray[1] for subarray in w_evolve]
    third_values = [subarray[2] for subarray in w_evolve]
    fourth_values = [subarray[3] for subarray in w_evolve]
    
    
    # Plot each variable against iterations
    plt.plot(iterations, first_values, label='Shaw')
    plt.plot(iterations, second_values, label='Random')
    plt.plot(iterations, third_values, label='Greedy')
    plt.plot(iterations, fourth_values, label='Regret-2')
    
    plt.xlabel('Iterations')
    plt.ylabel('Values')
    plt.title('Variables vs Iterations')
    
    # Add legend
    plt.legend()
    
    plt.show()

#Solution Evolution Plots
def SolutionCostsPlot(max_iter, new_sol_cost_evolve, global_sol_cost_evolve, current_sol_cost_evolve):
    
    iterations = list(range(1, max_iter+1))    
    
    # Plot each variable against iterations
    plt.plot(iterations, new_sol_cost_evolve, label='Cost of New Solution')
    plt.plot(iterations, current_sol_cost_evolve, label='Cost of Current Solution')
    plt.plot(iterations, global_sol_cost_evolve, label='Cost of Global Best Solutio')
    
    plt.xlabel('Iteration')
    plt.ylabel('Cost')
    plt.title('Cost vs Iteration')
    
    # Add legend
    plt.legend()
    
    plt.show()




