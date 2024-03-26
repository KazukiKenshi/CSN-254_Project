// Import Three.js library
import * as THREE from 'three';
import * as Loader from 'three/addons/loaders/OBJLoader.js';

console.log("Hello world");

// Create a scene
const scene = new THREE.Scene();

// Create a camera
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 5;

// Create a renderer
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Create a loader
const loader = new Loader.OBJLoader();
const modelPath = document.getElementById('modelPath').innerText;

let model;
// Load a 3D model
loader.load(
    modelPath,
    function (object) {
        model = object;
        scene.add(object);
    },
    function (xhr) {
        console.log((xhr.loaded / xhr.total * 100) + '% loaded');
    },
    function (error) {
        console.error('Error loading model:', error);
    }
);

// Add lights
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
directionalLight.position.set(0, 1, 1);
scene.add(directionalLight);

// Render the scene
function animate() {
    requestAnimationFrame(animate);
    if(model){
        model.rotation.y += 0.01;
    }
    renderer.render(scene, camera);
}
animate();
