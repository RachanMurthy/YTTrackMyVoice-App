import os
from yttrackmyvoice.project_manager import start_new_project, continue_existing_project, start_project

if __name__ == "__main__":
    # Welcome message
    print("Welcome to the YouTube Audio Downloader!\n")
    print("This tool helps you download audio from YouTube videos and organizes them into folders.\n")
    
    # Validate input and call the appropriate function
    project_name = None
    while project_name is None:
        # Prompt user for project type
        project_type = ""
        while project_type not in ['1', '2']:
            print("\nPlease enter 1 to start a new project or 2 to continue an existing project.")
            project_type = input("Would you like to: \n"
                                "(1) Start a new project\n"
                                "(2) Continue an existing project\n"
                                "Please enter 1 or 2: ").strip()
        

        if project_type == '1':
            # Start a new project
            project_name = start_new_project()  
        elif project_type == '2':
            # Continue an existing project
            project_name = continue_existing_project()
    
    start_project(project_name)

    