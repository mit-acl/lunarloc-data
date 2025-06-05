from ._mocks import Transform


def transform_to_tuple(
    transform: Transform,
) -> tuple[float, float, float, float, float, float]:
    """Convert a carla transform to a tuple.

    Args:
        transform: The carla transform to convert.

    Returns:
        The tuple representation of the transform.
    """

    return (
        transform.location.x,
        transform.location.y,
        transform.location.z,
        transform.rotation.roll,
        transform.rotation.pitch,
        transform.rotation.yaw,
    )
