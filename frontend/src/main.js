import * as THREE from "three";

import { GLTFLoader } from
    "three/examples/jsm/loaders/GLTFLoader.js";


// ============================================================
// HTML ELEMENTS
// ============================================================

const sceneContainer =
    document.getElementById("scene");

const loading =
    document.getElementById("loading");

const scanLine =
    document.getElementById("scanLine");

const statusText =
    document.getElementById("statusText");


// ============================================================
// CHECK SCENE CONTAINER
// ============================================================

if (!sceneContainer) {

    console.error(
        "ERROR: #scene was not found in index.html"
    );

}


// ============================================================
// THREE.JS SCENE
// ============================================================

const scene = new THREE.Scene();

scene.background =
    new THREE.Color(0x02060b);


// ============================================================
// CAMERA
// ============================================================

const camera =
    new THREE.PerspectiveCamera(
        35,
        window.innerWidth /
        window.innerHeight,
        0.01,
        100
    );

camera.position.set(
    0,
    0.15,
    6.8
);

camera.lookAt(
    0,
    0,
    0
);


// ============================================================
// RENDERER
// ============================================================

const renderer =
    new THREE.WebGLRenderer({

        antialias: true,

        alpha: true,

        powerPreference: "high-performance"

    });


renderer.setPixelRatio(

    Math.min(
        window.devicePixelRatio,
        2
    )

);


renderer.setSize(

    window.innerWidth,
    window.innerHeight

);


renderer.outputColorSpace =
    THREE.SRGBColorSpace;


renderer.setClearColor(
    0x02060b,
    1
);


sceneContainer.appendChild(
    renderer.domElement
);


// ============================================================
// LIGHTS
// ============================================================

const ambientLight =
    new THREE.AmbientLight(
        0x8fefff,
        2.5
    );

scene.add(
    ambientLight
);


const frontLight =
    new THREE.DirectionalLight(
        0x00eaff,
        4
    );

frontLight.position.set(
    0,
    2,
    5
);

scene.add(
    frontLight
);


const leftLight =
    new THREE.PointLight(
        0x0066ff,
        3,
        15
    );

leftLight.position.set(
    -4,
    1,
    5
);

scene.add(
    leftLight
);


const rightLight =
    new THREE.PointLight(
        0x00ffff,
        3,
        15
    );

rightLight.position.set(
    4,
    1,
    5
);

scene.add(
    rightLight
);


// ============================================================
// FACE GROUP
// ============================================================

const faceGroup =
    new THREE.Group();

scene.add(
    faceGroup
);


// ============================================================
// FACE MODEL
// ============================================================

let humanFace = null;


// ============================================================
// FACE BOUNDING BOX
// ============================================================

const faceBox =
    new THREE.Box3();

const projected =
    new THREE.Vector3();


// ============================================================
// LOAD GLB
// ============================================================

const loader =
    new GLTFLoader();


console.log(
    "Loading 3D face from /face.glb ..."
);


loader.load(

    "/face.glb",


    // ========================================================
    // SUCCESS
    // ========================================================

    function (gltf) {

        console.log(
            "================================="
        );

        console.log(
            "3D FACE LOADED SUCCESSFULLY"
        );

        console.log(
            "================================="
        );


        humanFace =
            gltf.scene;


        // ----------------------------------------------------
        // IMPORTANT:
        // REMOVE OLD TRANSFORM
        // ----------------------------------------------------

        humanFace.position.set(
            0,
            0,
            0
        );

        humanFace.rotation.set(
            0,
            0,
            0
        );

        humanFace.scale.set(
            1,
            1,
            1
        );


        // ----------------------------------------------------
        // ADD TO GROUP
        // ----------------------------------------------------

        faceGroup.add(
            humanFace
        );


        // ----------------------------------------------------
        // CALCULATE ORIGINAL MODEL SIZE
        // ----------------------------------------------------

        const originalBox =
            new THREE.Box3().setFromObject(
                humanFace
            );


        const originalSize =
            new THREE.Vector3();


        originalBox.getSize(
            originalSize
        );


        const originalCenter =
            new THREE.Vector3();


        originalBox.getCenter(
            originalCenter
        );


        console.log(
            "Original model size:",
            originalSize
        );


        // ----------------------------------------------------
        // CENTER MODEL
        // ----------------------------------------------------

        humanFace.position.sub(
            originalCenter
        );


        // ----------------------------------------------------
        // AUTO SCALE
        //
        // This prevents the face from being too
        // large or too small.
        // ----------------------------------------------------

        const largestDimension =
            Math.max(

                originalSize.x,

                originalSize.y,

                originalSize.z

            );


        if (
            largestDimension > 0
        ) {

            const targetHeight =
                2.8;


            const autoScale =
                targetHeight /
                largestDimension;


            humanFace.scale.set(
                autoScale,
                autoScale,
                autoScale
            );

        }


        // ----------------------------------------------------
        // MATERIAL + WIREFRAME
        // ----------------------------------------------------

        humanFace.traverse(

            function (object) {

                if (
                    !object.isMesh
                ) {

                    return;

                }


                // --------------------------------------------
                // SOLID FACE
                // --------------------------------------------

                object.material =
                    new THREE.MeshStandardMaterial({

                        color: 0x071923,

                        metalness: 0.25,

                        roughness: 0.55,

                        transparent: false,

                        opacity: 1

                    });


                // --------------------------------------------
                // WIREFRAME
                // --------------------------------------------

                const wireGeometry =
                    new THREE.WireframeGeometry(
                        object.geometry
                    );


                const wireMaterial =
                    new THREE.LineBasicMaterial({

                        color: 0x00eaff,

                        transparent: true,

                        opacity: 0.70

                    });


                const wireframe =
                    new THREE.LineSegments(

                        wireGeometry,

                        wireMaterial

                    );


                wireframe.scale.set(
                    1.002,
                    1.002,
                    1.002
                );


                object.add(
                    wireframe
                );

            }

        );


        // ----------------------------------------------------
        // FINAL CENTERING AFTER SCALING
        // ----------------------------------------------------

        const finalBox =
            new THREE.Box3().setFromObject(
                humanFace
            );


        const finalCenter =
            new THREE.Vector3();


        finalBox.getCenter(
            finalCenter
        );


        humanFace.position.x -=
            finalCenter.x;


        humanFace.position.y -=
            finalCenter.y;


        humanFace.position.z -=
            finalCenter.z;


        // ----------------------------------------------------
        // MOVE FACE SLIGHTLY DOWN
        // ----------------------------------------------------

        humanFace.position.y =
            -0.15;


        // ----------------------------------------------------
        // MAKE SURE FACE IS VISIBLE
        // ----------------------------------------------------

        humanFace.visible =
            true;


        faceGroup.visible =
            true;


        // ----------------------------------------------------
        // HIDE LOADING MESSAGE
        // ----------------------------------------------------

        if (loading) {

            loading.style.display =
                "none";

        }


        if (statusText) {

            statusText.textContent =
                "SCANNING FACE...";

        }


        console.log(
            "FACE IS NOW PERMANENTLY VISIBLE"
        );

    },


    // ========================================================
    // LOADING PROGRESS
    // ========================================================

    function (progress) {

        if (
            loading &&
            progress.total > 0
        ) {

            const percentage =
                Math.round(

                    (
                        progress.loaded /
                        progress.total

                    ) * 100

                );


            loading.textContent =
                "LOADING 3D FACE " +
                percentage +
                "%";

        }

    },


    // ========================================================
    // ERROR
    // ========================================================

    function (error) {

        console.error(
            "================================="
        );

        console.error(
            "3D FACE MODEL ERROR"
        );

        console.error(
            error
        );

        console.error(
            "================================="
        );


        if (loading) {

            loading.textContent =
                "3D FACE MODEL ERROR";

        }


        if (statusText) {

            statusText.textContent =
                "FACE MODEL ERROR";

        }

    }

);


// ============================================================
// SCAN LINE FUNCTION
// ============================================================

function updateScanLine() {

    if (
        !humanFace ||
        !scanLine
    ) {

        return;

    }


    // --------------------------------------------------------
    // GET CURRENT FACE BOUNDS
    // --------------------------------------------------------

    faceBox.setFromObject(
        humanFace
    );


    const min =
        faceBox.min;

    const max =
        faceBox.max;


    // --------------------------------------------------------
    // FACE CORNERS
    // --------------------------------------------------------

    const corners = [

        new THREE.Vector3(
            min.x,
            min.y,
            min.z
        ),

        new THREE.Vector3(
            min.x,
            min.y,
            max.z
        ),

        new THREE.Vector3(
            min.x,
            max.y,
            min.z
        ),

        new THREE.Vector3(
            min.x,
            max.y,
            max.z
        ),

        new THREE.Vector3(
            max.x,
            min.y,
            min.z
        ),

        new THREE.Vector3(
            max.x,
            min.y,
            max.z
        ),

        new THREE.Vector3(
            max.x,
            max.y,
            min.z
        ),

        new THREE.Vector3(
            max.x,
            max.y,
            max.z
        )

    ];


    let top =
        Infinity;

    let bottom =
        -Infinity;

    let left =
        Infinity;

    let right =
        -Infinity;


    // --------------------------------------------------------
    // PROJECT FACE TO SCREEN
    // --------------------------------------------------------

    for (
        const point of corners
    ) {

        projected.copy(
            point
        );


        projected.project(
            camera
        );


        const screenX =
            (
                projected.x *
                0.5 +
                0.5
            ) *
            window.innerWidth;


        const screenY =
            (
                -projected.y *
                0.5 +
                0.5
            ) *
            window.innerHeight;


        top =
            Math.min(
                top,
                screenY
            );


        bottom =
            Math.max(
                bottom,
                screenY
            );


        left =
            Math.min(
                left,
                screenX
            );


        right =
            Math.max(
                right,
                screenX
            );

    }


    // --------------------------------------------------------
    // FACE SIZE
    // --------------------------------------------------------

    const faceWidth =
        right - left;

    const faceHeight =
        bottom - top;


    if (
        faceWidth <= 0 ||
        faceHeight <= 0
    ) {

        return;

    }


    // --------------------------------------------------------
    // FACE CENTER
    // --------------------------------------------------------

    const centerX =
        (
            left +
            right
        ) / 2;


    // --------------------------------------------------------
    // SCAN POSITION
    //
    // Continuous top -> bottom -> top
    // --------------------------------------------------------

    const time =
        performance.now() *
        0.001;


    const progress =
        (
            Math.sin(
                time * 1.5
            ) +
            1
        ) / 2;


    const scanTop =
        top +
        faceHeight *
        0.20;


    const scanBottom =
        bottom -
        faceHeight *
        0.20;


    const scanY =
        scanTop +
        (
            scanBottom -
            scanTop
        ) *
        progress;


    // --------------------------------------------------------
    // SCAN WIDTH
    // --------------------------------------------------------

    const scanWidth =
        Math.max(

            180,

            Math.min(

                300,

                faceWidth *
                0.80

            )

        );


    // --------------------------------------------------------
    // APPLY POSITION
    // --------------------------------------------------------

    scanLine.style.left =
        centerX + "px";


    scanLine.style.top =
        scanY + "px";


    scanLine.style.width =
        scanWidth + "px";


    scanLine.style.display =
        "block";

}


// ============================================================
// ANIMATION
// ============================================================

function animate() {

    requestAnimationFrame(
        animate
    );


    // --------------------------------------------------------
    // ONE-DIRECTION ROTATION
    //
    // NEVER uses sin/cos for rotation.
    // Therefore rotation is always forward.
    // --------------------------------------------------------

    if (humanFace) {
        faceGroup.rotation.y += 0.025;
    }




    // --------------------------------------------------------
    // SCAN LINE
    // --------------------------------------------------------

    updateScanLine();


    // --------------------------------------------------------
    // RENDER
    // --------------------------------------------------------

    renderer.render(
        scene,
        camera
    );

}


// ============================================================
// START ANIMATION IMMEDIATELY
// ============================================================

animate();


// ============================================================
// RESIZE
// ============================================================

window.addEventListener(

    "resize",

    function () {

        camera.aspect =
            window.innerWidth /
            window.innerHeight;


        camera.updateProjectionMatrix();


        renderer.setSize(

            window.innerWidth,

            window.innerHeight

        );

    }

);


// ============================================================
// TAKE ATTENDANCE BUTTON
// ============================================================
const API_BASE = "http://127.0.0.1:5000";

// Helper elements
const addStudentModal = document.getElementById("addStudentModal");
const addStudentForm = document.getElementById("addStudentForm");
const cancelStudentBtn = document.getElementById("cancelStudentBtn");
const statusOverlay = document.getElementById("statusOverlay");
const statusOverlayMsg = document.getElementById("statusOverlayMsg");
const statusSpinner = document.getElementById("statusSpinner");
const closeStatusBtn = document.getElementById("closeStatusBtn");
const dashboardModal = document.getElementById("dashboardModal");
const closeDashboardBtn = document.getElementById("closeDashboardBtn");

// New Camera Elements
// New Camera Elements
const statusTitle = document.getElementById("statusTitle");
const cameraFeedContainer = document.getElementById("cameraFeedContainer");
const webcamVideo = document.getElementById("webcamVideo");
const webcamCanvas = document.getElementById("webcamCanvas");
const cancelScanBtn = document.getElementById("cancelScanBtn");

// WebRTC Stream Management
let webcamStream = null;
let webcamActive = false;
let webcamAnimationId = null;
let activeFaceBox = null;
let activeAttendanceStatus = "";

async function startWebcam() {
    if (webcamActive) return;
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480, facingMode: "user" },
            audio: false
        });
        if (webcamVideo) {
            webcamVideo.srcObject = webcamStream;
            webcamVideo.play();
        }
        webcamActive = true;
        renderWebcamLoop();
    } catch (err) {
        console.error("Error accessing webcam:", err);
        showStatus("WEBCAM ACCESS ERROR:<br>Please ensure camera permissions are granted.", false, true);
    }
}

function stopWebcam() {
    webcamActive = false;
    if (webcamAnimationId) {
        cancelAnimationFrame(webcamAnimationId);
        webcamAnimationId = null;
    }
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
    if (webcamVideo) {
        webcamVideo.srcObject = null;
    }
    if (webcamCanvas) {
        const ctx = webcamCanvas.getContext("2d");
        ctx.clearRect(0, 0, webcamCanvas.width, webcamCanvas.height);
    }
    activeFaceBox = null;
    activeAttendanceStatus = "";
}

function renderWebcamLoop() {
    if (!webcamActive) return;
    if (webcamVideo && webcamCanvas) {
        const ctx = webcamCanvas.getContext("2d");
        
        if (webcamCanvas.width !== webcamVideo.videoWidth) {
            webcamCanvas.width = webcamVideo.videoWidth || 640;
            webcamCanvas.height = webcamVideo.videoHeight || 480;
        }

        // Draw video frame mirrored for natural camera view
        ctx.save();
        ctx.translate(webcamCanvas.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(webcamVideo, 0, 0, webcamCanvas.width, webcamCanvas.height);
        ctx.restore();

        drawClientScanline(ctx, webcamCanvas.width, webcamCanvas.height);

        if (activeFaceBox) {
            const [x, y, w, h] = activeFaceBox;
            // Calculate mirrored X coordinate so bounding boxes overlay correctly on the mirrored video
            const mirroredX = webcamCanvas.width - x - w;

            ctx.strokeStyle = "#00ffe1";
            ctx.lineWidth = 3;
            ctx.strokeRect(mirroredX, y, w, h);

            const labelHeight = 35;
            ctx.fillStyle = "rgba(2, 6, 11, 0.85)";
            ctx.fillRect(mirroredX, y - labelHeight, w, labelHeight);
            ctx.strokeStyle = "#00ffe1";
            ctx.lineWidth = 1;
            ctx.strokeRect(mirroredX, y - labelHeight, w, labelHeight);

            ctx.fillStyle = "#00ffe1";
            ctx.font = "bold 18px Courier New";
            ctx.fillText(activeAttendanceStatus || "FACE DETECTED", mirroredX + 10, y - 11);
        }
    }
    webcamAnimationId = requestAnimationFrame(renderWebcamLoop);
}

let scanlineY = 0;
let scanlineDir = 1;
function drawClientScanline(ctx, width, height) {
    scanlineY += 4 * scanlineDir;
    if (scanlineY >= height) {
        scanlineY = height;
        scanlineDir = -1;
    } else if (scanlineY <= 0) {
        scanlineY = 0;
        scanlineDir = 1;
    }
    
    ctx.strokeStyle = "rgba(0, 254, 255, 0.8)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, scanlineY);
    ctx.lineTo(width, scanlineY);
    ctx.stroke();
}

function captureWebcamFrame() {
    if (!webcamCanvas || !webcamVideo) return null;
    const tempCanvas = document.createElement("canvas");
    tempCanvas.width = webcamVideo.videoWidth || 640;
    tempCanvas.height = webcamVideo.videoHeight || 480;
    const tempCtx = tempCanvas.getContext("2d");
    tempCtx.drawImage(webcamVideo, 0, 0, tempCanvas.width, tempCanvas.height);
    return tempCanvas.toDataURL("image/jpeg", 0.85);
}

// Helper to show/hide modals
function showModal(modal) {
    if (modal) modal.classList.add("active");
}
function hideModal(modal) {
    if (modal) modal.classList.remove("active");
}

// Helper to show status overlay with message and optional live camera
function showStatus(message, showSpinner = true, showClose = false, showCamera = false, showCancel = false) {
    if (statusOverlayMsg) statusOverlayMsg.innerHTML = message.replace(/\n/g, "<br>");
    if (statusSpinner) statusSpinner.style.display = showSpinner ? "block" : "none";
    if (closeStatusBtn) closeStatusBtn.style.display = showClose ? "block" : "none";
    
    if (statusTitle) statusTitle.style.display = showCamera ? "block" : "none";
    if (cameraFeedContainer) cameraFeedContainer.style.display = showCamera ? "block" : "none";
    if (cancelScanBtn) cancelScanBtn.style.display = showCancel ? "block" : "none";
    
    showModal(statusOverlay);
}

// Close status overlay
if (closeStatusBtn) {
    closeStatusBtn.addEventListener("click", () => {
        stopWebcam();
        hideModal(statusOverlay);
    });
}

// TAKE ATTENDANCE BUTTON
const attendanceBtn = document.getElementById("attendanceBtn");
if (attendanceBtn) {
    attendanceBtn.addEventListener("click", async function () {
        console.log("TAKE ATTENDANCE CLICKED");
        showStatus("Initializing camera scanner...<br>Look directly into the webcam.", true, false, true, true);
        
        await startWebcam();
        
        let isScanning = true;
        let scanTimeout = setTimeout(() => {
            isScanning = false;
            stopWebcam();
            showStatus("Attendance scan timed out.<br>No recognized faces found.", false, true);
        }, 15000);

        cancelScanBtn.onclick = () => {
            isScanning = false;
            clearTimeout(scanTimeout);
            stopWebcam();
            showStatus("Attendance scan cancelled.", false, true);
        };

        while (isScanning) {
            const frameData = captureWebcamFrame();
            if (!frameData) {
                await new Promise(r => setTimeout(r, 200));
                continue;
            }

            try {
                const response = await fetch(`${API_BASE}/api/recognize_frame`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ image: frameData })
                });
                const data = await response.json();

                if (data.success && isScanning) {
                    if (data.detected) {
                        activeFaceBox = data.box;
                        if (data.recognized) {
                            activeAttendanceStatus = `${data.name} (${data.match}%)`;
                            if (data.confirmed) {
                                isScanning = false;
                                clearTimeout(scanTimeout);
                                stopWebcam();
                                showStatus(`IDENTITY VERIFIED!<br><br>Name: ${data.name}<br>Roll: ${data.roll_number}<br>Status: ${data.attendance}`, false, true);
                                break;
                            }
                        } else {
                            activeAttendanceStatus = "UNKNOWN IDENTITY";
                        }
                    } else {
                        activeFaceBox = null;
                        activeAttendanceStatus = "";
                    }
                }
            } catch (err) {
                console.error(err);
            }

            await new Promise(r => setTimeout(r, 350));
        }
    });
}

// ADD STUDENT BUTTON
const addStudentBtn = document.getElementById("addStudentBtn");
if (addStudentBtn) {
    addStudentBtn.addEventListener("click", function () {
        console.log("ADD STUDENT CLICKED");
        if (addStudentForm) addStudentForm.reset();
        showModal(addStudentModal);
    });
}

if (cancelStudentBtn) {
    cancelStudentBtn.addEventListener("click", function () {
        hideModal(addStudentModal);
    });
}

if (addStudentForm) {
    addStudentForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        hideModal(addStudentModal);

        const name = document.getElementById("studentName").value;
        const roll_number = document.getElementById("rollNumber").value;
        const registration_number = document.getElementById("regNumber").value;

        showStatus("Saving student info & initiating camera capture...<br>Look at the camera.<br><br>CAPTURING FACE: 0%", true, false, true, true);

        await startWebcam();

        let frameIndex = 0;
        const totalFrames = 40;
        let isRegistering = true;

        cancelScanBtn.onclick = () => {
            isRegistering = false;
            stopWebcam();
            showStatus("Registration cancelled.", false, true);
        };

        while (frameIndex < totalFrames && isRegistering) {
            const frameData = captureWebcamFrame();
            if (!frameData) {
                await new Promise(r => setTimeout(r, 200));
                continue;
            }

            const pct = Math.round((frameIndex / totalFrames) * 100);
            showStatus(`Saving student info & initiating camera capture...<br>Look at the camera.<br><br><span style="font-size: 20px; font-weight: bold; color: #fff; text-shadow: 0 0 10px #00ffe1;">CAPTURING FACE: ${pct}%</span>`, true, false, true, true);

            try {
                const response = await fetch(`${API_BASE}/api/register_frame`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        name,
                        roll_number,
                        registration_number,
                        image: frameData,
                        frame_index: frameIndex,
                        total_frames: totalFrames
                    })
                });
                const data = await response.json();

                if (data.success && isRegistering) {
                    frameIndex++;
                    activeFaceBox = [160, 120, 320, 240]; // Center target box
                    activeAttendanceStatus = `CAPTURED (${frameIndex}/${totalFrames})`;
                } else if (isRegistering) {
                    showStatus(`Saving student info & initiating camera capture...<br><span style="color:#ff3333;">${data.message || 'Face not detected'}</span><br><br><span style="font-size: 20px; font-weight: bold; color: #fff; text-shadow: 0 0 10px #00ffe1;">CAPTURING FACE: ${pct}%</span>`, true, false, true, true);
                    activeFaceBox = null;
                    activeAttendanceStatus = "";
                }
            } catch (err) {
                console.error(err);
            }

            await new Promise(r => setTimeout(r, 250));
        }

        if (isRegistering) {
            stopWebcam();
            showStatus(`REGISTRATION SUCCESSFUL!<br><br>Name: ${name}<br>Roll: ${roll_number}<br>Model status: Trained successfully.`, false, true);
        }
    });
}

// CHECK ATTENDANCE BUTTON (DASHBOARD)
const checkBtn = document.getElementById("checkBtn");
if (checkBtn) {
    checkBtn.addEventListener("click", async function () {
        console.log("CHECK ATTENDANCE CLICKED");
        showStatus("Loading attendance data...", true, false);

        try {
            // Fetch Stats
            const statsRes = await fetch(`${API_BASE}/api/attendance/stats`);
            const stats = await statsRes.json();

            if (stats.success) {
                document.getElementById("statTotalStudents").textContent = stats.total_students;
                document.getElementById("statPresentToday").textContent = stats.present_today;
                document.getElementById("statAttendanceRate").textContent = `${stats.attendance_percentage}%`;
            }

            // Fetch Students List
            const studentsRes = await fetch(`${API_BASE}/api/students`);
            const studentsData = await studentsRes.json();
            const studentsBody = document.getElementById("studentsTableBody");
            
            if (studentsBody && studentsData.success) {
                studentsBody.innerHTML = "";
                if (studentsData.students.length === 0) {
                    studentsBody.innerHTML = `<tr><td colspan="3" style="text-align: center; padding: 20px;">No students registered yet</td></tr>`;
                } else {
                    studentsData.students.forEach(student => {
                        const tr = document.createElement("tr");
                        tr.innerHTML = `
                            <td>${student.name}</td>
                            <td>${student.roll_number}</td>
                            <td>${student.registration_number || 'N/A'}</td>
                        `;
                        studentsBody.appendChild(tr);
                    });
                }
            }

            // Fetch Attendance Records
            const attendanceRes = await fetch(`${API_BASE}/api/attendance`);
            const attendanceData = await attendanceRes.json();
            const attendanceBody = document.getElementById("attendanceTableBody");

            if (attendanceBody && attendanceData.success) {
                attendanceBody.innerHTML = "";
                if (attendanceData.attendance.length === 0) {
                    attendanceBody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 20px;">No attendance logs today</td></tr>`;
                } else {
                    attendanceData.attendance.forEach(record => {
                        const tr = document.createElement("tr");
                        tr.innerHTML = `
                            <td>${record.name}</td>
                            <td>${record.roll_number}</td>
                            <td>${record.time}</td>
                            <td style="color: #00ffe1;">${record.status}</td>
                        `;
                        attendanceBody.appendChild(tr);
                    });
                }
            }

            hideModal(statusOverlay);
            showModal(dashboardModal);

        } catch (error) {
            console.error(error);
            showStatus("CONNECTION ERROR:<br>Could not fetch dashboard statistics.", false, true);
        }
    });
}

if (closeDashboardBtn) {
    closeDashboardBtn.addEventListener("click", function () {
        hideModal(dashboardModal);
    });
}

// DEBUG MESSAGE
console.log(
    "SMART ATTENDANCE AI FRONTEND STARTED"
);

console.log(
    "3D MODEL PATH: /face.glb"
);