import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 0;

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const loader = new GLTFLoader();
const modelPath = document.getElementById("modelPath").textContent;
let model;
let mixer;

loader.load(
    modelPath,
    function (gltf) {
        model = gltf.scene;

        scene.add(model);
        model.position.z = -5;
        mixer = new THREE.AnimationMixer(model);
        gltf.animations.forEach((clip) => {
            const action = mixer.clipAction(clip);
            action.timeScale = 0; // Adjust this value to control the speed of the animation
            action.play();
        });
    },
    undefined,
    function (error) {
        console.error('Error loading GLTF model', error);
    }
);

const directionalLight = new THREE.DirectionalLight(0xffffff, 5);
directionalLight.position.set(0, 5, 0);
scene.add(directionalLight);

const ambientLight = new THREE.AmbientLight(0xffffff, 0);
scene.add(ambientLight);

function animate() {
    requestAnimationFrame(animate);
    const deltaTime = clock.getDelta();
    if (mixer) {
        mixer.update(deltaTime);
    }
    renderer.render(scene, camera);
}

animate();
