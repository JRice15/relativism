# Relativism Objects

src.rel_objects

Relativism Objects must inherit from either RelSavedObj (which are saved
in their own file) or RelContainerObj (which are smaller data containers
usually stored in their parent's file). Either may also inherit from 
RelPublicObj if the object should be directly processable by the user

## Saved

Objects (usually public) that are saved to files

Implement:
- `save` (if any additional file saving needed beyond save_metadata)
- `parse_write_meta`: dict -> dict with attrs added/removed (for save_metadata)
- `rename` (that calls super, and only handles renaming extra files)
- `file_ref_repr` (if you dont want the standard name.reltype)
- `validate_child_name`: -> bool

Notes:
- mode arg default must be "load"

## Container

These are simpler containers of data, that don't have children. They are saved
in a more compact format in the file of their parent, or in their own file if
there is a set of them all of the same class

Implement:
- `file_ref_data` and its inverse `load`



## Public

These objects are directly editable by the user, via `@public_process` methods

in the docstring of the public processes, give relevant info in the following format:


cat: {category: edit|meta|info|save|effect|other}  
desc: {a description to be displayed to the user}  
args:  
&ensp;&ensp;{argname}: {argument description for user}; {hidden data relevant to arg for various
purposes, such as Recording's random_method()}  
dev: {this line and all the rest below it will not be visible to the user, and are used for
developer notes}

Square brackets [] around the whole line of an argument signal that it is an optional argument

Argument type checking and conversion can be done by the `@public_process` decorator as well:

`@public_process("mode1", "mode2", "mode3", allowed=([mode1-low, mode1-high], ..., "mode3-allowed-chars"))`

Where modes1-3 are inpt_validate modes, that correspond to the same positional
arguments in the decorated function. "allowed" is a tuple of allowed values,
which accepts 'None' for any argument without an "allowed", or at most one Ellipsis 
(...) for multiple arguments in a row without "allowed"

