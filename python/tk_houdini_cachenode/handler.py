import os

import hou
import sgtk


class TkCacheNodeHandler(object):
    TK_CACHE_NODE_TYPE = "sgtk_cache"
    NODE_OUTPUT_PATH_PARM = "file"

    def __init__(self, app):
        self._app = app

    def setup_node(self, node):
        default_name = self._app.get_setting("default_node_name")
        node.setName(default_name, unique_name=True)

        try:
            self._app.log_metric("Create", log_version=True)
        except:
            # ingore any errors. ex: metrics logging not supported
            pass

    @classmethod
    def get_nodes(cls):
        """
        Returns a list of all tk-houdini-cachenode instances in the current
        session.
        """

        # get all instances of tk cache sop nodes
        return hou.nodeType(
            hou.sopNodeTypeCategory(), TkCacheNodeHandler.TK_CACHE_NODE_TYPE
        ).instances()

    @classmethod
    def get_output_path(cls, node):
        """
        Returns the evaluated output path for the supplied node.
        """

        output_parm = node.parm(cls.NODE_OUTPUT_PATH_PARM)
        path = output_parm.menuLabels()[output_parm.eval()]
        return path

    # refresh the output profile path
    def refresh_output_path(self, node):
        output_path_parm = node.parm(self.NODE_OUTPUT_PATH_PARM)
        output_path_parm.set(output_path_parm.eval())

    @classmethod
    def get_output_range(cls, node: hou.Node) -> list[int]:
        """This function returns our frame range or a single frame."""
        time_dependent = node.parm("timedependent").eval()
        framerange_type = node.parm("trange").eval()

        if time_dependent:
            if framerange_type > 0:
                start_frame = int(node.parm("f1").eval())
                end_frame = int(node.parm("f2").eval())
                framerange = [start_frame, end_frame]
            else:
                current_frame = int(hou.frame())
                framerange = [current_frame, current_frame]
        else:
            current_frame = int(node.parm("static_frame").eval())
            framerange = [current_frame, current_frame]

        return framerange

    # private methods

    def _getHipfileFields(self):

        # get the correct fields for the current hipfile
        current_filepath = hou.hipFile.path()
        work_template = self._app.get_template("work_file_template")

        # Set fields
        fields = work_template.get_fields(current_filepath)

        return fields

    def _computeOutputPath(self, node):

        # compute the output path based on the current work file and cache template

        # get relevant fields from the current file path
        work_file_fields = self._getHipfileFields()

        if not work_file_fields:
            msg = "This Houdini file is not a Shotgun Toolkit work file! Save the file through Shotgun save and create the node again."
            hou.ui.displayMessage(msg, buttons=("OK",), severity=hou.severityType.Error)
            raise sgtk.TankError(msg)

        time_dependent = node.parm("timedependent").eval()

        # Get the cache templates from the app
        output_cache_template = (
            self._app.get_template("output_cache_sequence_template")
            if time_dependent
            else self._app.get_template("output_cache_template")
        )

        # create fields dict with all the metadata
        fields = {
            "name": work_file_fields.get("name", None),
            "node": node.parm("name").eval(),
            "cache_version": node.parm("version").eval(),
            "version": node.parm("version").eval(),
        }

        if time_dependent:
            fields["SEQ"] = "FORMAT: $F"

        if node.parm("use_sg_version").eval():
            fields["version"] = work_file_fields.get("name", None)

        # update those fields with the output template
        fields.update(self._app.context.as_template_fields(output_cache_template))

        path = output_cache_template.apply_fields(fields)
        path = path.replace(os.path.sep, "/")

        return path
