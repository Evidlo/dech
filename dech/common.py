#!/usr/bin/env python3

from functools import wraps

def torch2np(args, selected_args, device):
    """Convert a tensor to numpy array"""
    import torch as t
    for selected_arg in selected_args:
        if type(args[selected_arg]) is t.Tensor:
            # save device of last detected tensor
            device = args[selected_arg].device.type
            args[selected_arg] = args[selected_arg].detach().cpu().numpy()

    return args, device

def np2torch(item, device):
    """Convert numpy array to tensor"""
    import torch as t
    import numpy as np
    if type(item) is np.ndarray:
        return t.from_numpy(item).to(device=device)
    elif type(item) is t.Tensor:
        return item.to(device)
    elif item is None:
        return
    else:
        return item
        # raise ValueError(f"Unknown item type {type(item)}.  Expected numpy array or pytorch tensor")

def handle_torch(args=None, kwargs=None, ret_args=None):
    """Automatically convert from pytorch tensor to numpy array when function is
    called and convert back when function returns

    If any of the selected input arguments are a tensor, convert them to ndarray
    and convert the selected return values back to tensors. If neither `args`
    nor `kwargs` are given, try to convert any torch Tensor
    we see.

    Args:
        args (list of int): positional arguments to convert
        kwargs (list of str): keyword arguments to convert
        ret_args (list of int): position return values to convert back

    Returns:
        function which handles CUDA tensors

    Usage:
        @handle_torch()
        def my_func(foo):
            ...
            return result_ndarray

        >>> my_func(input_tensor)
        result_tensor

        >>> my_func(input_ndarray)
        result_ndarray

        @handle_torch(args=[0], kwargs=['bar'])
        def my_func2(foo, bar=None):
            ...
            return some_ndarray
    """


    def decorator(func):
        @wraps(func)
        def wrapper(*f_args, **f_kwargs):
            f_args = list(f_args)
            device = None

            # ----- Calling -----

            # if no positional/keyword arguments selected, use all
            if args is None and kwargs is None:
                selected_args = range(len(f_args))
                selected_kwargs = f_kwargs.keys()
            else:
                selected_args = args
                selected_kwargs = kwargs
            # convert requested args from cuda
            if selected_args is not None:
                f_args, device = torch2np(f_args, selected_args, device)

            # convert requested kwargs from cuda
            if selected_kwargs is not None:
                f_kwargs, device = torch2np(f_kwargs, selected_kwargs, device)


            # call the function
            old_return = func(*f_args, **f_kwargs)

            # ----- Returning -----

            # if any of the inputs were pytorch tensors, convert the selected return values to tensors
            if device is not None:
                if ret_args is not None:
                    assert type(old_return) is tuple, "Function {func.__name__} should have returned multiple arguments"
                    new_return = list(old_return)
                    for arg in ret_args:
                        new_return[arg] = np2torch(old_return[arg], device)
                else:
                    if type(old_return) is tuple:
                        new_return = [np2torch(item, device) for item in old_return]
                    else:
                        new_return = np2torch(old_return, device)
            else:
                new_return = old_return

            return new_return

        return wrapper

    return decorator
