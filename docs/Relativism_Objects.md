# Relativism Objects

src.object_data

## Saved

Objects (usually public) that are saved to files

Implement:
- `save` (if any additional file saving needed beyond save_metadata)
- `parse_write_meta`: dict -> dict with attrs added/removed (for save_metadata)
- `rename` (that calls super, and only handles renaming extra files)
- `file_ref_repr` (if you dont want the standard name.reltype)
- `validate_child_name`: -> bool

## Container

These are simpler containers of data, that don't have children. They are saved
in a more compact format in the file of their parent, or in their own file if
there is a set of them all of the same class

Implement:
- `file_ref_data` and its inverse `load`

