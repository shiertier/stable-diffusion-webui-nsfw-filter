<<<<<<< HEAD
import launch

if not launch.is_installed("diffusers"):
    launch.run_pip(f"install diffusers", "diffusers")

if not launch.is_installed("imgutils"):
    launch.run_pip(f"install imgutils", "imgutils")
=======
import launch

if not launch.is_installed("diffusers"):
    launch.run_pip(f"install diffusers", "diffusers")
>>>>>>> eb139152b1f52fab3dedc59ab9fc68357bb502bd
