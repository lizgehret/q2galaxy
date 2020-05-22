import os
import distutils

import qiime2.sdk
import qiime2.plugin


def import_data(type, input_path, input_format):
    if input_format == '':
        input_format = None

    try:
        artifact = qiime2.sdk.Artifact.import_data(type, input_path,
                                                   view_type=input_format)
    except qiime2.plugin.ValidationError as e:
        raise ValueError(
            f'There was a problem importing {input_path}: ') from e
    except Exception as e:
        raise ValueError('An unexpected error has occurred:') from e

    if input_format is None:
        input_format = artifact.format.__name__

    return artifact


# TODO: We probably want to be able to export history items and export that
# stuff to the history
def export_data(input_path, output_path, output_format):
    if output_format == '':
        output_format = None
    result = qiime2.sdk.Result.load(input_path)
    if output_format is None:
        if isinstance(result, qiime2.sdk.Artifact):
            output_format = result.format.__name__
        else:
            output_format = 'Visualization'
        result.export_data(output_path)
    else:
        if isinstance(result, qiime2.sdk.Visualization):
            raise ValueError(
                "'output_format' cannot be used with visualizations")
        else:
            source = result.view(qiime2.sdk.parse_format(output_format))
            if os.path.isfile(str(source)):
                if os.path.isfile(output_path):
                    os.remove(output_path)
                elif os.path.dirname(output_path) == '':
                    # This allows the user to pass a filename as a path if they
                    # want their output in the current working directory
                    output_path = os.path.join('.', output_path)
                if os.path.dirname(output_path) != '':
                    # create directory (recursively) if it doesn't exist yet
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                qiime2.util.duplicate(str(source), output_path)
            else:
                distutils.dir_util.copy_tree(str(source), output_path)


builtin_map = {
    'import_data': import_data,
    'export_data': export_data
}
