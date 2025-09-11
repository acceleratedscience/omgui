def is_running_in_jupyter():
    """
    Checks if the script is running inside a Jupyter Notebook or Lab.
    Returns True if in a Jupyter environment, False otherwise.
    """
    try:
        # Import the kernel app, which is unique to Jupyter
        from IPython import get_ipython

        # Check for the presence of the 'IPKernelApp' class
        if "IPKernelApp" in get_ipython().config:
            return True
        else:
            return False
    except (ImportError, AttributeError):
        # The above will fail if get_ipython is not available or not a kernel
        return False
