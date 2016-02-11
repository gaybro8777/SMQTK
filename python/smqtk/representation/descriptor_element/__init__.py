import abc
import numpy
import os

from smqtk.representation import SmqtkRepresentation
from smqtk.utils import plugin
from smqtk.utils import merge_dict


__author__ = "paul.tunison@kitware.com"


class DescriptorElement (SmqtkRepresentation, plugin.Pluggable):
    """
    Abstract descriptor vector container.

    This structure supports implementations that cache descriptor vectors on a
    per-UUID basis.

    UUIDs must maintain unique-ness when transformed into a string.

    Descriptor element equality based on shared descriptor type and vector
    equality. Two descriptor vectors that are generated by different types of
    descriptor generator should not be considered the same (though, this may be
    up for discussion).

    Stored vectors should be effectively immutable.

    """

    def __init__(self, type_str, uuid):
        """
        Initialize a new descriptor element.

        :param type_str: Type of descriptor. This is usually the name of the
            content descriptor that generated this vector.
        :type type_str: str

        :param uuid: Unique ID reference of the descriptor.
        :type uuid: collections.Hashable

        """
        super(DescriptorElement, self).__init__()

        self._type_label = type_str
        self._uuid = uuid

    def __hash__(self):
        return hash((self.type(), self.uuid()))

    def __eq__(self, other):
        if isinstance(other, DescriptorElement):
            b = self.vector() == other.vector()
            if isinstance(b, numpy.core.multiarray.ndarray):
                vec_equal = b.all()
            else:
                vec_equal = b
            return vec_equal and (self.type() == other.type())
        return False

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return "%s{type: %s, uuid: %s}" % (self.__class__.__name__, self.type(),
                                           self.uuid())

    @classmethod
    def get_default_config(cls):
        """
        Generate and return a default configuration dictionary for this class.
        This will be primarily used for generating what the configuration
        dictionary would look like for this class without instantiating it.

        By default, we observe what this class's constructor takes as arguments,
        aside from the first two assumed positional arguments, turning those
        argument names into configuration dictionary keys.
        If any of those arguments have defaults, we will add those values into
        the configuration dictionary appropriately.
        The dictionary returned should only contain JSON compliant value types.

        It is not be guaranteed that the configuration dictionary returned
        from this method is valid for construction of an instance of this class.

        :return: Default configuration dictionary for the class.
        :rtype: dict

        """
        # similar to parent impl, except we remove the ``type_str`` and ``uuid``
        # configuration parameters as they are to be specified at runtime.
        dc = super(DescriptorElement, cls).get_default_config()
        # These parameters must be specified at construction time.
        del dc['type_str'], dc['uuid']
        return dc

    # noinspection PyMethodOverriding
    @classmethod
    def from_config(cls, config_dict, type_str, uuid, merge_default=True):
        """
        Instantiate a new instance of this class given the desired type, uuid,
        and JSON-compliant configuration dictionary.

        :param type_str: Type of descriptor. This is usually the name of the
            content descriptor that generated this vector.
        :type type_str: str

        :param uuid: Unique ID reference of the descriptor.
        :type uuid: collections.Hashable

        :param config_dict: JSON compliant dictionary encapsulating
            a configuration.
        :type config_dict: dict

        :param merge_default: Merge the given configuration on top of the
            default provided by ``get_default_config``.
        :type merge_default: bool

        :return: Constructed instance from the provided config.
        :rtype: DescriptorElement

        """
        c = {}
        merge_dict(c, config_dict)
        c['type_str'] = type_str
        c['uuid'] = uuid
        return super(DescriptorElement, cls).from_config(c, merge_default)

    def uuid(self):
        """
        :return: Unique ID for this vector.
        :rtype: collections.Hashable
        """
        return self._uuid

    def type(self):
        """
        :return: Type label type of the DescriptorGenerator that generated this
            vector.
        :rtype: str
        """
        return self._type_label

    ###
    # Abstract methods
    #

    @abc.abstractmethod
    def has_vector(self):
        """
        :return: Whether or not this container current has a descriptor vector
            stored.
        :rtype: bool
        """

    @abc.abstractmethod
    def vector(self):
        """
        :return: Get the stored descriptor vector as a numpy array. This returns
            None of there is no vector stored in this container.
        :rtype: numpy.core.multiarray.ndarray or None
        """

    @abc.abstractmethod
    def set_vector(self, new_vec):
        """
        Set the contained vector.

        If this container already stores a descriptor vector, this will
        overwrite it.

        :param new_vec: New vector to contain.
        :type new_vec: numpy.core.multiarray.ndarray

        """


from ._io import *


def get_descriptor_element_impls(reload_modules=False):
    """
    Discover and return discovered ``DescriptorElement`` classes. Keys in the
    returned map are the names of the discovered classes, and the paired values
    are the actual class type objects.

    We search for implementation classes in:
        - modules next to this file this function is defined in (ones that begin
          with an alphanumeric character),
        - python modules listed in the environment variable ``DESCRIPTOR_ELEMENT_PATH``
            - This variable should contain a sequence of python module
              specifications, separated by the platform specific PATH separator
              character (``;`` for Windows, ``:`` for unix)

    Within a module we first look for a helper variable by the name
    ``DESCRIPTOR_ELEMENT_CLASS``, which can either be a single class object or
    an iterable of class objects, to be specifically exported. If the variable
    is set to None, we skip that module and do not import anything. If the
    variable is not present, we look at attributes defined in that module for
    classes that descend from the given base class type. If none of the above
    are found, or if an exception occurs, the module is skipped.

    :param reload_modules: Explicitly reload discovered modules from source.
    :type reload_modules: bool

    :return: Map of discovered class object of type ``DescriptorElement``
        whose keys are the string names of the classes.
    :rtype: dict[str, type]

    """
    this_dir = os.path.abspath(os.path.dirname(__file__))
    env_var = "DESCRIPTOR_ELEMENT_PATH"
    helper_var = "DESCRIPTOR_ELEMENT_CLASS"
    return plugin.get_plugins(__name__, this_dir, env_var, helper_var,
                              DescriptorElement, reload_modules)
