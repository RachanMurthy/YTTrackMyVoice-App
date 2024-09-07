import os
from yttrackmyvoice.utils import save_list_to_csv, load_list_from_csv, create_directory_if_not_exists

def start_new_project(data_directory='data'):
    """Handles the creation of a new project and stores the project name in a CSV file."""
    
    create_directory_if_not_exists(data_directory)

    # Path to the CSV file that will store all project names
    project_csv = os.path.join(data_directory, 'projects.csv')
    
    # Check if the CSV file exists, if not create it
    if not os.path.exists(project_csv):
        # Create an empty CSV file if it doesn't exist
        with open(project_csv, 'w', newline='') as file:
            pass  # Just creating the file, no data written yet

    # Load all project names from the CSV file
    project_names = load_list_from_csv(project_csv)

    while True:
        # Prompt user for a project name
        project_name = input("\nPlease enter a name for your new project: ").strip()

        # Replace spaces with underscores
        project_name = project_name.replace(" ", "_")
    
        # Check if any projects exist
        if project_name in project_names.values():
            print(f"\nA project with the name '{project_name}' already exists.")

            print("\nHere are the available projects:")
            for index, project in project_names.items():
                print(f"{index}. {project}")

            continue
        else:
            # If the project name doesn't exist, proceed with creating the new project
            print(f"\nGreat! A new project folder will be created as: {project_name}\n")

            # Append the project name to the CSV file
            save_list_to_csv([project_name], project_csv, "a")
            break  # Exit the loop when a valid new project name is provided

    return project_name


def continue_existing_project(data_directory='data'):
    """Handles continuing an existing project by displaying all project names."""
    
    # Path to the CSV file storing project names
    project_csv = os.path.join(data_directory, 'projects.csv')
    
    # Load all project names from the CSV file
    project_names = load_list_from_csv(project_csv)
    
    # Check if any projects exist
    if not project_names:
        print("\nNo projects found. Please start a new project first.")
        return None
    
    # Display the available projects
    print("\nHere are the available projects:")
    for index, project in project_names.items():
        print(f"{index+1}. {project}")
    
    # Prompt the user for the project name
    project_name = input("\nPlease enter the name of the project you want to continue: ").strip()
    
    # Check if the entered project exists
    if project_name in project_names.values():
        print(f"\nContinuing with the existing project: {project_name}\n")
    else:
        print(f"\nNo project found with the name '{project_name}'. Please make sure to enter a valid project name.")
        project_name = None  # Return None if the project doesn't exist
    
    return project_name
