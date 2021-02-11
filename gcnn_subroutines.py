import numpy as np


def remove_element(L,arr):
    ind = 0
    size = len(L)
    while ind != size and not np.array_equal(L[ind],arr):
        ind += 1
    if ind != size:
        L.pop(ind)
    else:
        raise ValueError('array not found in list.')
        

# Centroid Neural Networks with Detected Weights
def centroid_neural_network_detected_weights(input_data, detected_weights, n_clusters, epochs = 10):
    X = input_data
    w = detected_weights
    initial_clusters = len(w)


    cluster_elements = []
    for cluster in range(initial_clusters):
        cluster_i = []
        cluster_elements.append(cluster_i)

    cluster_lengths = np.zeros(initial_clusters, dtype=int)
    cluster_indices = []


    for i in range(len(X)):
        x = X[i]

        distances = []
        for w_i in w:
            dist = np.linalg.norm(x-w_i)
            distances.append(dist)

        # find winner neuron
        index = np.argmin(distances)

        # add cluster index of data x to a list
        cluster_indices.append(index)

        # update winner neuron
        w[index] = w[index] + 1/(1+cluster_lengths[index])*(x - w[index])

        # append data to cluster
        cluster_elements[index].append(x)
        cluster_lengths[index] += 1

    centroids = []
    for elements in cluster_elements:
        elements = np.array(elements)
        centroid_i = np.average(elements[:, -len(elements[0]):], axis=0)
        centroids.append(centroid_i)

    for epoch in range(epochs):
        loser = 0

        for i in range(len(X)):
            x = X[i]

            distances = []
            for w_i in w:
                dist = np.linalg.norm(x-w_i)
                distances.append(dist)

            # find winner neuron of x
            current_cluster_index = np.argmin(distances)

            # what was the winner for x in previous epoch
            x_th = i
            previous_cluster_index = cluster_indices[x_th]

            # check if current neuron is a loser
            if previous_cluster_index != current_cluster_index:
                # update winner neuron
                w[current_cluster_index] = w[current_cluster_index] + (x - w[current_cluster_index])/(cluster_lengths[current_cluster_index]+1)

                # update loser neuron
                w[previous_cluster_index] = w[previous_cluster_index] - (x - w[previous_cluster_index])/(cluster_lengths[previous_cluster_index]-1)

                # add and remove data to cluster    
                cluster_elements[current_cluster_index] = list(cluster_elements[current_cluster_index])
                cluster_elements[current_cluster_index].append(x)
                remove_element(cluster_elements[previous_cluster_index], x)  

                # update cluster index
                cluster_indices[x_th] = current_cluster_index

                cluster_lengths[current_cluster_index] += 1
                cluster_lengths[previous_cluster_index] -= 1

                loser += 1

        centroids = []
        for elements in cluster_elements:
            elements = np.array(elements)
            centroid_i = np.average(elements[:, -len(elements[0]):], axis=0)
            centroids.append(centroid_i)

        print(epoch+1, len(centroids))

        if loser == 0: 
            if len(w) == n_clusters:
                print("Reach the Desired Number of Clusters. Stop at Epoch ", epoch+1)
                break

            else:
                all_error = []
                for i in range(len(centroids)):

                    # calculate error
                    error = 0
                    for x in cluster_elements[i]:

                        dist_e = np.linalg.norm(x-centroids[i])
                        error += dist_e

                    all_error.append(error)

                splitted_index = np.argmax(all_error)

                new_w = w[splitted_index] + epsilon
                w.append(new_w)

                new_cluster_thing = []
                new_cluster_thing = np.array(new_cluster_thing)

                cluster_elements.append(new_cluster_thing)

                cluster_lengths = list(cluster_lengths)
                cluster_lengths.append(0)
                cluster_lengths = np.array(cluster_lengths)

    return centroids, w, cluster_indices, cluster_elements


# G-CNN
def g_centroid_neural_network(input_data, num_clusters, num_subdata = 10, max_iteration = 50, epsilon = 0.05):

    X = input_data
    new_data = []
    for i in range(num_subdata):
        subdata = []
        for j in range(len(X)//num_subdata):
            x_i = X[(len(X)//num_subdata)*i + j]
            subdata.append(x_i)
        new_data.append(subdata)
    new_data = np.array(new_data)
    # print(np.array(new_data).shape)

    centroids = []
    w = []
    cluster_indices = []
    cluster_elements = []

    for i in range(len(new_data)):
        subdata_i = new_data[i]

        centroids_, w_, cluster_indices_, cluster_elements_ = centroid_neural_network(subdata_i, num_clusters, max_iteration, epsilon)

        centroids.append(centroids_)
        w.append(w_)
        cluster_indices.append(cluster_indices_)
        cluster_elements.append(cluster_elements_)

    # Create New Data with Detected Centroids
    gen2_data = []
    for centroids_i in centroids:
        for centroid_ii in centroids_i: 
            gen2_data.append(centroid_ii)

    gen2_data = np.array(gen2_data)

    # Run G-CNN one more time
    centroids_2, w_2, cluster_indices_2, cluster_elements_2 = centroid_neural_network(gen2_data, num_clusters, max_iteration, epsilon)

    # Run G-CNN last time
    detected_weights = centroids_2
    centroids, weights, cluster_indices, cluster_elements = centroid_neural_network_detected_weights(X, detected_weights, num_clusters, max_iteration)
    print("Reach the Desired Number of Clusters. Stop!")
    
    return centroids, weights, cluster_indices, cluster_elements