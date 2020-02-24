# Contribute to Noteworthy

Before contributing to this repository, you might want to check out the [README](../README.md)'s last section that highlights which areas need improvement.

Please make sure the following points are kept in mind before contributing:
- **Make sure the existing functionalities do not break after incorporating your features or bug removals.**
- [options.json](../options.json) file plays a critical role in the user's interaction with the app. While I would advice against changing anything in the existing options, adding new options would also mean validating those options. The validation happens in the `check_options` function of [app.py](../app.py), so make sure to add those validations before adding your functionality.
- Keep the app as ligheweight as possible. For example, I have used the models with FP16 precision levels instead of their FP32 counterparts even though I'm possibly getting lower accuracy, just so to keep the size of the app to a bare minimum.
- Make sure no bad coding practise is followed. The code readability is one of the top priorities.


With all that in mind, follow the steps below for contribution.

1. Fork this repo, and clone the forked repo.
2. Create a new branch with the following naming convention:
    ```sh
    git branch <username>_new_<feature_added>  # for new feature
    # OR
    git branch <username>_fix_<bug_fixed>  # for bug removals
    ```
    For example:
    ```sh
    git branch rafi007akhtar_new_visualizer  # for new feature
    # OR
    git branch rafi007akhtar_fix_latency  # for bug removals
    ```
3. Checkout to your branch, 
    ```sh
    git checkout <branch_name>
    ```
    and add your changes.
4. Push your branch
    ```sh
    git push origin <branch_name>
    ```
5. Make a Pull Request.
