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

        faceGroup.rotation.y +=
            0.006;

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
const statusTitle = document.getElementById("statusTitle");
const cameraFeedContainer = document.getElementById("cameraFeedContainer");
const cameraFeed = document.getElementById("cameraFeed");
const cancelScanBtn = document.getElementById("cancelScanBtn");

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
    
    if (showCamera) {
        if (cameraFeed && cameraFeed.src !== `${API_BASE}/api/video_feed`) {
            cameraFeed.src = `${API_BASE}/api/video_feed`;
        }
    } else {
        if (cameraFeed) cameraFeed.src = "";
    }
    showModal(statusOverlay);
}

// Close status overlay
if (closeStatusBtn) {
    closeStatusBtn.addEventListener("click", () => hideModal(statusOverlay));
}

// Cancel scan event listener
if (cancelScanBtn) {
    cancelScanBtn.addEventListener("click", async () => {
        showStatus("Cancelling scan...", true, false, false, false);
        try {
            await fetch(`${API_BASE}/api/camera/cancel`, { method: "POST" });
        } catch (e) {
            console.error(e);
        }
    });
}

// TAKE ATTENDANCE BUTTON
const attendanceBtn = document.getElementById("attendanceBtn");
if (attendanceBtn) {
    attendanceBtn.addEventListener("click", async function () {
        console.log("TAKE ATTENDANCE CLICKED");
        showStatus("Initializing system camera scanner...<br>Look directly into the webcam.", true, false, true, true);

        try {
            const response = await fetch(`${API_BASE}/api/recognition`);
            const data = await response.json();

            if (data.success) {
                if (data.recognized) {
                    showStatus(
                        `IDENTITY VERIFIED!<br><br>Name: ${data.name}<br>Roll: ${data.roll_number}<br>Status: ${data.attendance}`,
                        false,
                        true,
                        false,
                        false
                    );
                } else {
                    showStatus(`RECOGNITION FAILED:<br>${data.message || 'Face not recognized'}`, false, true, false, false);
                }
            } else {
                showStatus(`ERROR: ${data.message || 'Verification error'}`, false, true, false, false);
            }
        } catch (error) {
            console.error(error);
            showStatus("FAILED TO CONNECT TO BACKEND SERVER", false, true, false, false);
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

        // Start progress polling
        let progressInterval = setInterval(async () => {
            try {
                const res = await fetch(`${API_BASE}/api/register/progress/${roll_number}`);
                const data = await res.json();
                if (data.success) {
                    showStatus(`Saving student info & initiating camera capture...<br>Look at the camera.<br><br><span style="font-size: 20px; font-weight: bold; color: #fff; text-shadow: 0 0 10px #00ffe1;">CAPTURING FACE: ${data.progress}%</span>`, true, false, true, true);
                }
            } catch (e) {
                console.error("Error fetching registration progress:", e);
            }
        }, 400);

        try {
            const response = await fetch(`${API_BASE}/api/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ name, roll_number, registration_number })
            });
            clearInterval(progressInterval);
            const data = await response.json();

            if (data.success) {
                showStatus(
                    `REGISTRATION SUCCESSFUL!<br><br>Name: ${data.name}<br>Roll: ${data.roll_number}<br>Images Captured: ${data.images}<br>Model status: Trained`,
                    false,
                    true,
                    false,
                    false
                );
            } else {
                showStatus(`REGISTRATION FAILED:<br>${data.message || 'Could not complete registration'}`, false, true, false, false);
            }
        } catch (error) {
            clearInterval(progressInterval);
            console.error(error);
            showStatus("CONNECTION ERROR:<br>Could not reach backend server.", false, true, false, false);
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