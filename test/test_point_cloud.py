import inspect
from pathlib import Path

import open3d as o3d
import numpy as np
import skimage.io

from disparity_view.util import dummy_pinhole_camera_intrincic

tum_data = o3d.data.SampleTUMRGBDImage()
depth_path = tum_data.depth_path
color_path = tum_data.color_path


def test_t_point_cloud():
    """
    o3d.t を利用するデータ構造ベースでのpoint_cloud の使い方を確認するためのコード
    """
    print(f"{depth_path=}")
    print(f"{color_path=}")
    device = o3d.core.Device("CPU:0")
    depth = o3d.t.io.read_image(depth_path).to(device)
    color = o3d.t.io.read_image(color_path).to(device)

    width = color.columns
    height = color.rows

    intrinsic = o3d.core.Tensor([[535.4, 0, 320.1], [0, 539.2, 247.6], [0, 0, 1]])
    rgbd = o3d.t.geometry.RGBDImage(color, depth)

    pcd = o3d.t.geometry.PointCloud.create_from_rgbd_image(rgbd, intrinsic, depth_scale=5000.0, depth_max=10.0)

    assert hasattr(pcd, "project_to_rgbd_image")
    assert isinstance(intrinsic, o3d.core.Tensor)
    rgbd_reproj = pcd.project_to_rgbd_image(width, height, intrinsic, depth_scale=5000.0, depth_max=10.0)

    assert hasattr(rgbd_reproj, "color")
    assert hasattr(rgbd_reproj, "depth")

    color_legacy = np.asarray(rgbd_reproj.color.to_legacy())
    depth_legacy = np.asarray(rgbd_reproj.depth.to_legacy())

    assert isinstance(color_legacy, np.ndarray)
    assert isinstance(depth_legacy, np.ndarray)

    assert color_legacy.shape[0] == height
    assert color_legacy.shape[1] == width
    assert color_legacy.dtype == np.float32

    assert depth_legacy.shape[0] == height
    assert depth_legacy.shape[1] == width
    assert depth_legacy.dtype == np.float32


def test_point_cloud():
    """
    o3d.t を利用するデータ構造ベースでのpoint_cloud の使い方を確認するためのコード
    """
    depth = o3d.io.read_image(depth_path)
    color = o3d.io.read_image(color_path)

    height, width = np.array(color).shape[:2]

    intrinsic = o3d.core.Tensor([[535.4, 0, 320.1], [0, 539.2, 247.6], [0, 0, 1]])
    """
    wrong code:
    No such constructor
    o3d.geometry.RGBDImage(color, depth)
    """
    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(color, depth)

    assert isinstance(rgbd, o3d.geometry.RGBDImage)
    intrinsic = dummy_pinhole_camera_intrincic((height, width))

    assert isinstance(intrinsic, o3d.cpu.pybind.camera.PinholeCameraIntrinsic)

    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, intrinsic)
    if 0:
        for k, v in inspect.getmembers(pcd):
            if str(v).find("method") > -1:
                print(f"{k=} {v=}")

    assert hasattr(pcd, "project_to_rgbd_image") == False

    """
    o3d.geometry.PointCloud 型に再投影するためのメソッドは見つからなかった。
    """


if __name__ == "__main__":

    test_t_point_cloud()

    test_point_cloud()