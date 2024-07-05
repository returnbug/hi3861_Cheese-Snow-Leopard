<template>
    <div>
    </div>
</template>


<script setup>
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { PCDLoader } from 'three/addons/loaders/PCDLoader.js';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { onUnmounted } from 'vue'

const router = useRouter();

const back =()=>{
    router.push('/table')
}

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(80, window.innerWidth / window.innerHeight, 0.01, 10000000);
camera.position.set(0, 0, 0.3);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);

var gui = new GUI();
var attributesFolder = gui.addFolder('点云设置');
gui.domElement.style.left = '0px';


const buttonConfig = { 返回: back }
gui.add(buttonConfig, '返回').name('返回')


function resetGUI() {
    // 删除之前的GUI
    gui.destroy();

    // 创建一个新的GUI实例
    gui = new GUI();
    // gui.add(isRotation, 'bool').name('旋转');
    attributesFolder = gui.addFolder('点云设置');
    gui.domElement.style.left = '0px';

}

// 创建四个透视相机 ———— 作为生成该点云的相机展示
var helpCamera = [];
for (let i = 0; i < 4; i++) {
    helpCamera[i] = new THREE.PerspectiveCamera(60, 1, 0.1, 0.4);
    scene.add(helpCamera[i]);
}

// 用SfM中de'dao定义相机变换矩阵，并应用到相应的相机上
const transformMatrix0 = new THREE.Matrix4();
transformMatrix0.set(
    0.9635227966591445, -0.0298251417806896, -0.2659591721221557, -3.1861460134378618,
    0.04168012934974072, 0.9983679551673119, 0.03904091331448917, -0.0658694912288581,
    0.264360714054735, -0.04870202267670474, 0.963193400024973, 1.701830863209624117,
    0, 0, 0, 1
);
helpCamera[0].applyMatrix4(transformMatrix0);

const transformMatrix1 = new THREE.Matrix4();
transformMatrix1.set(
    0.8671344194352608, -0.01285630331924969, -0.4979082386300075, -1.981515886805006,
    0.03166906549661311, 0.9990671872561505, 0.02935686697614572, -0.0212592897059282,
    0.4970663626933977, -0.04122463842227529, 0.8667326925100427, 2.75149718348900723,
    0, 0, 0, 1
);
helpCamera[1].applyMatrix4(transformMatrix1);

const transformMatrix2 = new THREE.Matrix4();
transformMatrix2.set(
    0.7024094659673048, -0.007144654873624021, -0.711737238049452, -2.685856668225444,
    0.09031055886130245, 0.9927625554048429, 0.07916130079909767, -0.0514197827631538,
    0.7060204990492023, -0.1198810347502172, 0.6979710541487608, 2.332535510893329,
    0, 0, 0, 1
);
helpCamera[2].applyMatrix4(transformMatrix2);

const transformMatrix3 = new THREE.Matrix4();
transformMatrix3.set(
    0.5308375671028522, 0.00925889315102485, -0.8474230054995811, -3.381832006499801,
    0.1320681431688673, 0.9868199683489367, 0.09351125936341173, -0.0917595736102196,
    0.8371197542241209, -0.1615568722321077, 0.5226183063406084, 1.036010012067961,
    0, 0, 0, 1
);
helpCamera[3].applyMatrix4(transformMatrix3);


const helpers = [];

let url = ref('')
url = sessionStorage.getItem('url')
const urlObject = new URL(url)
const pathname = urlObject.pathname
const segments = pathname.split('/')
const imageName = segments[segments.length - 1]
const name = imageName.split('.')[0]

// 创建点云加载器
const loader = new PCDLoader();
// 加载点云模型
loader.load("http://127.0.0.1:80/getPCD/" + name, function (points) {
    // 将点云几何居中并绕X轴旋转180度
    points.geometry.center();
    points.geometry.rotateX(Math.PI);

    // 创建点云材质，vertexColors 设置为 true 以显示顶点颜色
    const material = new THREE.PointsMaterial({ size: 0.004, vertexColors: true });

    // 创建点云对象
    const pointCloud = new THREE.Points(points.geometry, material);
    scene.add(pointCloud);

    // 使四个相机朝向点云
    for (let i = 0; i < helpCamera.length; i++) {
        helpCamera[i].lookAt(pointCloud.position);
    }

    // 在 GUI 中添加点云相关设置
    const folder = attributesFolder.addFolder(`点云 `);
    const text = { pointsNum: points.geometry.attributes.position.count};

    console.log(points.geometry.attributes.color);

    
    folder.add(text, 'pointsNum').name('点数');
    folder.add(material, 'size', 0, 0.1).name('点大小');
    folder.addColor(material, 'color').name('点颜色').onChange(function () {
        material.needsUpdate = true;
    });
    folder.add(material, 'vertexColors').name('显示顶点颜色').onChange(function () {
        material.needsUpdate = true; // 需要手动更新材质，否则没作用
    });

    // 为每个相机创建CameraHelper对象并显示出来
    const helpers = [];
    for (let i = 0; i < 4; i++) {
        helpers[i] = new THREE.CameraHelper(helpCamera[i]);
        scene.add(helpers[i]);
        helpers[i].visible = false;
    }
});


// 用于控制是否旋转的变量
const isRotation = { bool: false };

// onresize 事件会在窗口被调整大小时发生
window.onresize = function () {
    // 重置渲染器输出画布，相机
    renderer.setSize(window.innerWidth, window.innerHeight);
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
};

function animate() {
    // 如果 isRotation.bool 为真，则在每一帧中旋转场景
    if (isRotation.bool) {
        scene.rotation.y += 0.005;
    }

    // 渲染场景
    renderer.render(scene, camera);

    // 通过递归调用自身，实现持续动画
    requestAnimationFrame(animate);
}

// 初始调用动画函数
animate();

onUnmounted(() => {
    if (gui) {
        gui.destroy()
    }

    if (renderer) {
        document.body.removeChild(renderer.domElement)
    }
})

</script>
<style scoped></style>