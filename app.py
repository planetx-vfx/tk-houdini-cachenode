"""
File Cache node App for use with Toolkit's Houdini engine.
"""

import hou
import sgtk


class TkCacheNodeApp(sgtk.platform.Application):
    def init_app(self):
        """Initialize the app."""

        tk_houdini_cachenode = self.import_module("tk_houdini_cachenode")
        self.handler = tk_houdini_cachenode.TkCacheNodeHandler(self)

    def setup_node(self, node: hou.Node):
        """
        Set up the supplied node on creation.
        """
        return self.handler.setup_node(node)

    def get_nodes(self):
        """
        Returns a list of hou.node objects for each tk cache node.
        Example usage::
        >>> import sgtk
        >>> eng = sgtk.platform.current_engine()
        >>> app = eng.apps["tk-houdini-cache"]
        >>> tk_cache_nodes = app.get_nodes()
        """

        self.log_debug("Retrieving tk-houdini-cache nodes...")
        nodes = self.handler.get_nodes()
        self.log_debug("Found %s tk-houdini-cache nodes." % (len(nodes),))
        return nodes

    def get_output_path(self, node: hou.Node):
        """
        Returns the evaluated output path for the supplied node.
        Example usage::
        >>> import sgtk
        >>> eng = sgtk.platform.current_engine()
        >>> app = eng.apps["tk-houdini-cachenode"]
        >>> output_path = app.get_output_path(tk_cache_node)
        """

        self.log_debug("Retrieving output path for %s" % (node,))
        output_path = self.handler.get_output_path(node)
        self.log_debug("Retrieved output path: %s" % (output_path,))
        return output_path

    def refresh_output_path(self, node: hou.Node):
        """
        Refreshes the output path for the supplied node.
        """
        return self.handler.refresh_output_path(node)

    def get_output_range(self, node: hou.Node) -> list[int]:
        """Get output frame range for the supplied node

        Args:
            node (hou.Node): SGTK Cache node
        """
        return self.handler.get_output_range(node)

    def get_work_file_template(self):
        """
        Returns the configured work file template for the app.
        """

        return self.get_template("work_file_template")

    def get_node_render_template(self, node: hou.Node):
        """
        Returns the configured cache file template for the app.

        Args:
            node (hou.Node): SGTK Cache node
        """

        time_dependent = node.parm("timedependent").eval()

        # Get the cache templates from the app
        return (
            self.get_template("output_cache_sequence_template")
            if time_dependent
            else self.get_template("output_cache_template")
        )

    def get_node_publish_template(self, node: hou.Node):
        """
        Returns the configured publish file template for the app.

        Args:
            node (hou.Node): SGTK Cache node
        """

        time_dependent = node.parm("timedependent").eval()

        # Get the cache templates from the app
        return (
            self.get_template("output_publish_sequence_template")
            if time_dependent
            else self.get_template("output_publish_template")
        )
