import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { Mic, Power } from 'lucide-react';

const DEFAULT_THEME = {
  primary: '#00e5ff',
  glow: '#0088ff',
  secondary: '#80f7ff'
};

const AGENT_THEMES = {
  nexus: DEFAULT_THEME,
  codeforge: { primary: '#3b82f6', glow: '#1d4ed8', secondary: '#93c5fd' },
  voicepulse: { primary: '#00ff88', glow: '#00cc66', secondary: '#a3ffce' },
  synapse: { primary: '#00e5ff', glow: '#0088ff', secondary: '#80f7ff' },
  scribe: { primary: '#00e5ff', glow: '#0088ff', secondary: '#80f7ff' }
};

export default function HologramSphere({ computing = false, agent = 'nexus', isListening = false, onMicToggle, scale = 1.0 }) {
  const mountRef = useRef(null);
  const activeColors = AGENT_THEMES[agent] || DEFAULT_THEME;

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    let animationFrameId;
    const width = container.clientWidth || 380;
    const height = container.clientHeight || 380;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 5.0); // Framed perfectly to show full 3D sphere

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enableZoom = false;
    controls.autoRotate = true;
    controls.autoRotateSpeed = isListening ? 5.0 : (computing ? 3.5 : 1.5);

    const mainColor = new THREE.Color(isListening ? '#ef4444' : activeColors.primary);

    const hudGroup = new THREE.Group();
    hudGroup.scale.set(scale, scale, scale);
    scene.add(hudGroup);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(mainColor, isListening ? 6 : 3, 20);
    pointLight.position.set(0, 0, 0);
    scene.add(pointLight);

    // 1. Inner Holographic Core (Wireframe Icosahedron)
    const coreGeom = new THREE.IcosahedronGeometry(0.55, 2);
    const coreMat = new THREE.MeshStandardMaterial({
      color: isListening ? 0xef4444 : 0x00f2fe,
      wireframe: true,
      transparent: true,
      opacity: 0.8,
      emissive: isListening ? 0xef4444 : 0x0088ff,
      emissiveIntensity: isListening ? 0.9 : 0.6
    });
    const coreMesh = new THREE.Mesh(coreGeom, coreMat);
    hudGroup.add(coreMesh);

    // 2. Particle Swarm Cloud Sphere (Multi-layered gradient)
    const particleCount = 950;
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const c1 = new THREE.Color(isListening ? '#ef4444' : '#00f2fe');
    const c2 = new THREE.Color(isListening ? '#ff7878' : '#a855f7');
    const c3 = new THREE.Color(isListening ? '#fcd34d' : '#38bdf8');

    for (let i = 0; i < particleCount; i++) {
      const u = Math.random();
      const v = Math.random();
      const theta = u * 2.0 * Math.PI;
      const phi = Math.acos(2.0 * v - 1.0);
      const r = 1.15 + (Math.random() - 0.5) * 0.35;

      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.sin(phi) * Math.sin(theta);
      const z = r * Math.cos(phi);

      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;

      const randVal = Math.random();
      const mixedColor = randVal < 0.5 ? c1.clone().lerp(c2, randVal * 2) : c2.clone().lerp(c3, (randVal - 0.5) * 2);
      colors[i * 3] = mixedColor.r;
      colors[i * 3 + 1] = mixedColor.g;
      colors[i * 3 + 2] = mixedColor.b;
    }

    const particlesGeom = new THREE.BufferGeometry();
    particlesGeom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particlesGeom.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const particlesMat = new THREE.PointsMaterial({
      size: 0.048,
      vertexColors: true,
      transparent: true,
      opacity: 0.85
    });

    const particleSphere = new THREE.Points(particlesGeom, particlesMat);
    hudGroup.add(particleSphere);

    // 3. Multi-Axial Gyroscopic Orbital Rings
    const ringMat1 = new THREE.MeshBasicMaterial({ color: isListening ? 0xef4444 : 0x00f2fe, wireframe: true, transparent: true, opacity: 0.75 });
    const ringMat2 = new THREE.MeshBasicMaterial({ color: isListening ? 0xff7878 : 0xa855f7, wireframe: true, transparent: true, opacity: 0.6 });
    const ringMat3 = new THREE.MeshBasicMaterial({ color: isListening ? 0xfcd34d : 0x38bdf8, wireframe: true, transparent: true, opacity: 0.5 });

    const ring1 = new THREE.Mesh(new THREE.TorusGeometry(1.5, 0.014, 16, 100), ringMat1);
    ring1.rotation.x = Math.PI / 3;
    hudGroup.add(ring1);

    const ring2 = new THREE.Mesh(new THREE.TorusGeometry(1.7, 0.012, 16, 100), ringMat2);
    ring2.rotation.y = Math.PI / 4;
    hudGroup.add(ring2);

    const ring3 = new THREE.Mesh(new THREE.TorusGeometry(1.9, 0.01, 16, 100), ringMat3);
    ring3.rotation.x = -Math.PI / 6;
    hudGroup.add(ring3);

    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();
      controls.update();

      const speedMult = isListening ? 2.5 : 1.0;
      ring1.rotation.z = elapsed * 0.4 * speedMult;
      ring2.rotation.x = elapsed * 0.3 * speedMult;
      ring3.rotation.y = elapsed * 0.5 * speedMult;
      coreMesh.rotation.y = elapsed * 0.6 * speedMult;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container || !renderer || !camera) return;
      const newW = container.clientWidth || 380;
      const newH = container.clientHeight || 380;
      if (newW > 0 && newH > 0) {
        camera.aspect = newW / newH;
        camera.updateProjectionMatrix();
        renderer.setSize(newW, newH);
      }
    };

    const resizeObserver = new ResizeObserver(() => {
      handleResize();
    });
    resizeObserver.observe(container);

    // Initial resize trigger after DOM layout frame
    setTimeout(handleResize, 50);

    let startX = 0;
    let startY = 0;
    let isClickCandidate = false;

    const handlePointerDown = (e) => {
      startX = e.clientX;
      startY = e.clientY;
      isClickCandidate = true;
    };

    const handlePointerUp = (e) => {
      if (!isClickCandidate) return;
      isClickCandidate = false;
      const dist = Math.hypot(e.clientX - startX, e.clientY - startY);
      if (dist < 6) {
        if (onMicToggle) onMicToggle();
      }
    };

    renderer.domElement.addEventListener('pointerdown', handlePointerDown);
    renderer.domElement.addEventListener('pointerup', handlePointerUp);

    return () => {
      renderer.domElement.removeEventListener('pointerdown', handlePointerDown);
      renderer.domElement.removeEventListener('pointerup', handlePointerUp);
      window.removeEventListener('resize', handleResize);
      resizeObserver.disconnect();
      cancelAnimationFrame(animationFrameId);
      controls.dispose();
      renderer.dispose();
      scene.clear();
    };
  }, [computing, agent, isListening, onMicToggle]);

  return (
    <div 
      className={`hologram-hud-box ${isListening ? 'hologram-listening' : ''}`}
      onClick={onMicToggle}
    >
      {/* 3D Canvas Mount Point */}
      <div className="hologram-canvas-container" ref={mountRef} />
    </div>
  );
}
