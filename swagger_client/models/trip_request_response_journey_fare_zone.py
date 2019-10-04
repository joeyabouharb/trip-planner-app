# coding: utf-8

"""
    Trip Planner

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class TripRequestResponseJourneyFareZone(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'net': 'str',
        'to_leg': 'int',
        'from_leg': 'int',
        'neutral_zone': 'str'
    }

    attribute_map = {
        'net': 'net',
        'to_leg': 'toLeg',
        'from_leg': 'fromLeg',
        'neutral_zone': 'neutralZone'
    }

    def __init__(self, net=None, to_leg=None, from_leg=None, neutral_zone=None):  # noqa: E501
        """TripRequestResponseJourneyFareZone - a model defined in Swagger"""  # noqa: E501

        self._net = None
        self._to_leg = None
        self._from_leg = None
        self._neutral_zone = None
        self.discriminator = None

        if net is not None:
            self.net = net
        if to_leg is not None:
            self.to_leg = to_leg
        if from_leg is not None:
            self.from_leg = from_leg
        if neutral_zone is not None:
            self.neutral_zone = neutral_zone

    @property
    def net(self):
        """Gets the net of this TripRequestResponseJourneyFareZone.  # noqa: E501

        Not currently used.  # noqa: E501

        :return: The net of this TripRequestResponseJourneyFareZone.  # noqa: E501
        :rtype: str
        """
        return self._net

    @net.setter
    def net(self, net):
        """Sets the net of this TripRequestResponseJourneyFareZone.

        Not currently used.  # noqa: E501

        :param net: The net of this TripRequestResponseJourneyFareZone.  # noqa: E501
        :type: str
        """

        self._net = net

    @property
    def to_leg(self):
        """Gets the to_leg of this TripRequestResponseJourneyFareZone.  # noqa: E501

        Not currently used.  # noqa: E501

        :return: The to_leg of this TripRequestResponseJourneyFareZone.  # noqa: E501
        :rtype: int
        """
        return self._to_leg

    @to_leg.setter
    def to_leg(self, to_leg):
        """Sets the to_leg of this TripRequestResponseJourneyFareZone.

        Not currently used.  # noqa: E501

        :param to_leg: The to_leg of this TripRequestResponseJourneyFareZone.  # noqa: E501
        :type: int
        """

        self._to_leg = to_leg

    @property
    def from_leg(self):
        """Gets the from_leg of this TripRequestResponseJourneyFareZone.  # noqa: E501

        Not currently used.  # noqa: E501

        :return: The from_leg of this TripRequestResponseJourneyFareZone.  # noqa: E501
        :rtype: int
        """
        return self._from_leg

    @from_leg.setter
    def from_leg(self, from_leg):
        """Sets the from_leg of this TripRequestResponseJourneyFareZone.

        Not currently used.  # noqa: E501

        :param from_leg: The from_leg of this TripRequestResponseJourneyFareZone.  # noqa: E501
        :type: int
        """

        self._from_leg = from_leg

    @property
    def neutral_zone(self):
        """Gets the neutral_zone of this TripRequestResponseJourneyFareZone.  # noqa: E501

        Not currently used.  # noqa: E501

        :return: The neutral_zone of this TripRequestResponseJourneyFareZone.  # noqa: E501
        :rtype: str
        """
        return self._neutral_zone

    @neutral_zone.setter
    def neutral_zone(self, neutral_zone):
        """Sets the neutral_zone of this TripRequestResponseJourneyFareZone.

        Not currently used.  # noqa: E501

        :param neutral_zone: The neutral_zone of this TripRequestResponseJourneyFareZone.  # noqa: E501
        :type: str
        """

        self._neutral_zone = neutral_zone

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(TripRequestResponseJourneyFareZone, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, TripRequestResponseJourneyFareZone):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other