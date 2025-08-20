import matplotlib.pyplot as plt
import numpy as np
import csv

def main():
    MIN = 0
    MAX = 1
    BINSIZE = 0.05
    MEAN_CUTOFF = 0.5

    intensity_thresh = 0.37
    activity_fraction_thresh = 0.1

    FILENAME = "Intensity_Results.csv"

    plt.rcParams['mathtext.fontset'] = 'stix'
    plt.rcParams['font.family'] = 'STIXGeneral'
    plt.rcParams['font.size'] = 13

    mean_intensities_dict = {}
    pixel_intensities_dict = {}

    with open(FILENAME, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Row is not empty and not first row:
            if len(row) >= 3 and row[2] != "Name":
                # Is name already included in mean_intensities_dict? If not, initialize list
                if not row[2] in mean_intensities_dict:
                    mean_intensities_dict[row[2]] = []
                
                # Append intensity to mean_intensities_dict
                mean_intensities_dict[row[2]].append(float(row[1]))
            
            if len(row) >= 4 and row[2] != "Name":
                if not row[2] in pixel_intensities_dict:
                    pixel_intensities_dict[row[2]] = []
                pixel_intensities_dict[row[2]].append(np.fromstring(row[3].strip('[]'), sep=',', dtype=float))
    
    # Find and print maximal and minimal intensities
    min_int = float("inf")
    max_int = 0
    for name in mean_intensities_dict:
        min_int = min(min_int, min(mean_intensities_dict[name]))
        max_int = max(max_int, max(mean_intensities_dict[name]))
    print(f"Intensity range: {min_int} - {max_int}")
    
    for name in mean_intensities_dict:
        # mean_intensities_dict[name] = filter_data(mean_intensities_dict[name], MIN, MAX)
        print_cell_stats(name, mean_intensities_dict[name], MEAN_CUTOFF)

    # Make plot for each dataset
    for name in mean_intensities_dict:
        plt.figure()
        bins = np.arange(MIN, MAX + BINSIZE/2.0 , BINSIZE)
        counts, bins, patches = plt.hist(mean_intensities_dict[name], bins=bins, edgecolor='black')
        plt.xticks(bins, rotation=45)  # Optional: rotate for readability
        plt.xlabel('Intensity')
        plt.ylabel('Occurences')
        plt.xlim(MIN, MAX)
        plt.title(name)
        plt.savefig(f"{name}.pdf")

    # Combine all datasets into single plot
    combined_list = []
    for lst in mean_intensities_dict.values():
        combined_list.extend(lst)
    plt.figure()
    bins = np.arange(MIN, MAX + BINSIZE/2.0 , BINSIZE)
    counts, bins, patches = plt.hist(combined_list, bins=bins, edgecolor='black')
    plt.xticks(bins, rotation=45)  # Optional: rotate for readability
    plt.xlabel('Intensity')
    plt.ylabel('Occurences')
    plt.xlim(MIN, MAX)
    plt.title("combined")
    plt.savefig(f"combined.pdf")


    # Make plot showing A vs G data
    plt.figure()
    data_blue = []
    data_red = []
    for name in mean_intensities_dict:
        if name[0] == "A":
            data_blue.extend(mean_intensities_dict[name])
        elif name[0] == "G":
            data_red.extend(mean_intensities_dict[name])

    print_cell_stats("A cells", data_blue, MEAN_CUTOFF)
    print_cell_stats("G cells", data_red, MEAN_CUTOFF)
    print_cell_stats("ALL", combined_list, MEAN_CUTOFF)

    # Stacked
    plt.figure()
    bins = np.arange(MIN, MAX + BINSIZE/2.0 , BINSIZE)
    counts, bins, patches = plt.hist([data_blue, data_red], bins=bins, label=["A", "G"], edgecolor='black', color=["blue", "red"], stacked=True)
    plt.xticks(bins, rotation=45)  # Optional: rotate for readability
    plt.xlabel('Intensity')
    plt.ylabel('Occurences')
    plt.xlim(MIN, MAX)
    plt.legend()
    plt.title("combined_A_vs_G_stacked")
    plt.savefig(f"combined_A_vs_G_stacked.pdf")

    # Not stacked
    plt.figure()
    bins = np.arange(MIN, MAX + BINSIZE/2.0 , BINSIZE)
    counts, bins, patches = plt.hist([data_blue, data_red], bins=bins, label=["A", "G"], edgecolor='black', color=["blue", "red"], stacked=False)
    plt.xticks(bins, rotation=45)  # Optional: rotate for readability
    plt.xlabel('Intensity')
    plt.ylabel('Occurences')
    plt.xlim(MIN, MAX)
    plt.legend()
    plt.title("combined_A_vs_G")
    plt.savefig(f"combined_A_vs_G.pdf")


    print("--------- num dark cells criterion ------------")
    pixel_fraction_dict = {}
    for name in pixel_intensities_dict:
        if not name in pixel_fraction_dict:
            pixel_fraction_dict[name] = []
        
        for pixel_list in pixel_intensities_dict[name]:
            frac = np.mean(pixel_list > intensity_thresh)
            pixel_fraction_dict[name].append(frac)
        
        plt.figure()
        bins = np.arange(MIN, MAX + BINSIZE/2.0 , BINSIZE)
        counts, bins, patches = plt.hist(pixel_fraction_dict[name], bins=bins, edgecolor='black', label=f"Pixel intensity cutoff = {intensity_thresh}")
        plt.xticks(bins, rotation=45)  # Optional: rotate for readability
        plt.xlabel('Fraction of active pixels')
        plt.ylabel('Number of ROIs')
        plt.xlim(MIN, MAX)
        plt.title(name)
        plt.savefig(f"Fractional {name}.pdf")

        active = int(np.sum(np.array(pixel_fraction_dict[name]) > activity_fraction_thresh))
        inactive = int(np.sum(np.array(pixel_fraction_dict[name]) <= activity_fraction_thresh))

        print(f"\"{name}\": Active: {active}, inactive: {inactive}. Percentage active: {100.0 * active / (active + inactive) :.1f}%.")


def filter_data(data, xmin, xmax):
    return [x for x in data if xmin <= x <= xmax]

def print_cell_stats(name, intensity_list, MEAN_CUTOFF):
    print(f"Name: \"{name}\", num cells: {len(intensity_list)}, num cells >{MEAN_CUTOFF} Intensity: {np.sum(np.array(intensity_list) > MEAN_CUTOFF)}, percentage {100 * np.sum(np.array(intensity_list) > MEAN_CUTOFF) / len(intensity_list):.1f}%")

if __name__ == "__main__":
    main()
