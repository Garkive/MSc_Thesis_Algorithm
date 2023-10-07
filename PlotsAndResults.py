#Development of final plots and results potentially to be incorporated in Main.py.

import matplotlib.pyplot as plt


#Weight Evolution Plots
def SimpleWeightsPlot(max_iter, w_evolve):
        
    iterations = list(range(1, max_iter+1))
            
    first_values = [subarray[0]/(subarray[0]+subarray[1]) for subarray in w_evolve]
    second_values = [subarray[1]/(subarray[0]+subarray[1]) for subarray in w_evolve]
    third_values = [subarray[2]/(subarray[2]+subarray[3]+subarray[4]+subarray[5]+subarray[6]) for subarray in w_evolve]
    fourth_values = [subarray[3]/(subarray[2]+subarray[3]+subarray[4]+subarray[5]+subarray[6]) for subarray in w_evolve]
    fifth_values = [subarray[4]/(subarray[2]+subarray[3]+subarray[4]+subarray[5]+subarray[6]) for subarray in w_evolve]
    sixth_values = [subarray[5]/(subarray[2]+subarray[3]+subarray[4]+subarray[5]+subarray[6]) for subarray in w_evolve]
    seventh_values = [subarray[6]/(subarray[2]+subarray[3]+subarray[4]+subarray[5]+subarray[6]) for subarray in w_evolve]
    
    first_values1 = [subarray[0] for subarray in w_evolve]
    second_values1 = [subarray[1] for subarray in w_evolve]
    third_values1 = [subarray[2] for subarray in w_evolve]
    fourth_values1 = [subarray[3] for subarray in w_evolve]
    fifth_values1 = [subarray[4] for subarray in w_evolve]
    sixth_values1 = [subarray[5] for subarray in w_evolve]
    seventh_values1 = [subarray[6] for subarray in w_evolve]
    
    # Plot each variable against iterations
    plt.plot(iterations, first_values, label='Shaw')
    plt.plot(iterations, second_values, label='Random-d')
    plt.plot(iterations, third_values, label='Greedy')
    plt.plot(iterations, fourth_values, label='Regret-2')
    plt.plot(iterations, fifth_values, label='Regret-3')
    plt.plot(iterations, sixth_values, label='Regret-4')
    plt.plot(iterations, seventh_values, label='Random-r')
    
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    
    axes[0].plot(iterations, first_values1, label='Shaw')
    axes[0].plot(iterations, second_values1, label='Random-d')
    axes[0].plot(iterations, third_values1, label='Greedy')
    axes[0].plot(iterations, fourth_values1, label='Regret-2')
    axes[0].plot(iterations, fifth_values1, label='Regret-3')
    axes[0].plot(iterations, sixth_values1, label='Regret-4')
    axes[0].plot(iterations, seventh_values1, label='Random-r')
    axes[0].set_xlabel('Iterations')
    axes[0].set_ylabel('Values')
    axes[0].set_title('Weights vs Iterations')
    axes[0].legend()
    
    axes[1].plot(iterations, first_values, label='Shaw')
    axes[1].plot(iterations, second_values, label='Random-d')
    axes[1].plot(iterations, third_values, label='Greedy')
    axes[1].plot(iterations, fourth_values, label='Regret-2')
    axes[1].plot(iterations, fifth_values, label='Regret-3')
    axes[1].plot(iterations, sixth_values, label='Regret-4')
    axes[1].plot(iterations, seventh_values, label='Random-r')
    axes[1].set_xlabel('Iterations')
    axes[1].set_ylabel('Values')
    axes[1].set_title('Relative Weights vs Iterations')
    axes[1].legend()
    
    plt.tight_layout()
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




