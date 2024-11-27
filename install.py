import launch

if not launch.is_installed("diffusers"):
    launch.run_pip(f"install diffusers", "diffusers")

if not launch.is_installed("imgutils"):
    launch.run_pip(f"install git+https://github.com/deepghs/imgutils.git@v0.7.0", "git+https://github.com/deepghs/imgutils.git@v0.7.0")
