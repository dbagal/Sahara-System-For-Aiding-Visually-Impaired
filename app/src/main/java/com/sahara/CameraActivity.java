package com.sahara;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.CameraX;
import androidx.camera.core.FlashMode;
import androidx.camera.core.ImageCapture;
import androidx.camera.core.ImageCaptureConfig;
import androidx.camera.core.ImageProxy;
import androidx.camera.core.Preview;
import androidx.camera.core.PreviewConfig;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import android.content.pm.PackageManager;
import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.Matrix;
import android.os.Bundle;
import android.util.Log;
import android.util.Rational;
import android.util.Size;
import android.view.Surface;
import android.view.TextureView;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.Toast;
import java.io.ByteArrayOutputStream;


public class CameraActivity extends AppCompatActivity {


    private int REQUEST_CODE_PERMISSIONS = 101;
    private final String[] REQUIRED_PERMISSIONS = new String[]{"android.permission.CAMERA"};
    TextureView textureView;
    ImageButton capture;

    public static String SERVER_IP;
    public static int SERVER_PORT;
    public static Communicate connObj;
    public static Communicate.SendData sendDataThread;
    public ImageCapture imgCap;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_camera);

        getSupportActionBar().hide();

        textureView = findViewById(R.id.view_finder);
        int size  = Resources.getSystem().getDisplayMetrics().widthPixels;
        textureView.getLayoutParams().width = size;
        textureView.getLayoutParams().height = size;

        if(allPermissionsGranted()){
            startCamera(); //start camera if permission has been granted by user
        } else{
            ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS);
        }

        SERVER_IP = "192.168.43.15";
        SERVER_PORT = 7000;

        connObj = new Communicate(SERVER_IP, SERVER_PORT);

    }

    private void screenTapListener()
    {
        if(connObj.connectionStatus.equals("SUCCESS"))
        {
            imgCap.takePicture(new ImageCapture.OnImageCapturedListener() {
                @Override
                public void onCaptureSuccess(ImageProxy image, int rotationDegrees) {
                    super.onCaptureSuccess(image, rotationDegrees);

                    Bitmap bitmap = textureView.getBitmap();
                    bitmap = Bitmap.createScaledBitmap(bitmap, 500, 500, true);

                    ByteArrayOutputStream baos=new ByteArrayOutputStream();
                    bitmap.compress(Bitmap.CompressFormat.PNG,100, baos);
                    byte [] imgBytes = baos.toByteArray();

                    sendDataThread = new Communicate.SendData(imgBytes);
                    sendDataThread.start();

                    String msg = connObj.getMessage();
                    Toast.makeText(getApplicationContext(), msg, Toast.LENGTH_LONG).show();
                }
            });
        }
        else
        {
            //Prompt for no connection
        }
    }


    /*-------------------------------------------------------------------------------------------------------------------------*/

    private boolean allPermissionsGranted(){
        for(String permission : REQUIRED_PERMISSIONS){
            if(ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED){
                return false;
            }
        }
        return true;
    }

    /*-------------------------------------------------------------------------------------------------------------------------*/

    private void startCamera() {

        CameraX.unbindAll();

        Size screen = new Size(textureView.getWidth(), textureView.getHeight()); //size of the screen


        PreviewConfig pConfig = new PreviewConfig.Builder()
                .setTargetAspectRatio(new Rational(1, 1))
                .setTargetResolution(screen)
                .build();
        Preview preview = new Preview(pConfig);


        preview.setOnPreviewOutputUpdateListener(
                new Preview.OnPreviewOutputUpdateListener() {
                    @Override
                    public void onUpdated(Preview.PreviewOutput output){
                        ViewGroup parent = (ViewGroup) textureView.getParent();
                        parent.removeView(textureView);
                        parent.addView(textureView, 0);

                        textureView.setSurfaceTexture(output.getSurfaceTexture());
                        updateTransform();
                    }
                });


        ImageCaptureConfig imageCaptureConfig = new ImageCaptureConfig.Builder()
                .setCaptureMode(ImageCapture.CaptureMode.MAX_QUALITY)
                .setFlashMode(FlashMode.AUTO)
                .setTargetRotation(getWindowManager()
                .getDefaultDisplay()
                .getRotation()).build();

        imgCap = new ImageCapture(imageCaptureConfig);

        capture = findViewById(R.id.imgCapture);
        capture.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                if(connObj.connectionStatus.equals("SUCCESS"))
                {
                    capture.setEnabled(false);

                    imgCap.takePicture(new ImageCapture.OnImageCapturedListener() {
                        @Override
                        public void onCaptureSuccess(ImageProxy image, int rotationDegrees) {
                            super.onCaptureSuccess(image, rotationDegrees);

                            Bitmap bitmap = textureView.getBitmap();
                            bitmap = Bitmap.createScaledBitmap(bitmap, 500, 500, true);

                            ByteArrayOutputStream baos=new ByteArrayOutputStream();
                            bitmap.compress(Bitmap.CompressFormat.PNG,100, baos);
                            byte [] imgBytes = baos.toByteArray();

                            sendDataThread = new Communicate.SendData(imgBytes);
                            sendDataThread.start();

                            String msg = connObj.getMessage();
                            Toast.makeText(getApplicationContext(), msg, Toast.LENGTH_LONG).show();
                        }
                    });
                    capture.setEnabled(true);
                }
                else
                {
                    //Prompt for no connection
                }
            }
        });

        //bind to lifecycle:
        CameraX.bindToLifecycle(this, preview, imgCap);
    }

    /*-------------------------------------------------------------------------------------------------------------------------*/

    private void updateTransform(){
        Matrix mx = new Matrix();
        float w = textureView.getMeasuredWidth();
        float h = textureView.getMeasuredHeight();

        float cX = w / 2f;
        float cY = h / 2f;

        int rotationDgr;
        int rotation = (int)textureView.getRotation();

        switch(rotation){
            case Surface.ROTATION_0:
                rotationDgr = 0;
                break;
            case Surface.ROTATION_90:
                rotationDgr = 90;
                break;
            case Surface.ROTATION_180:
                rotationDgr = 180;
                break;
            case Surface.ROTATION_270:
                rotationDgr = 270;
                break;
            default:
                return;
        }

        mx.postRotate((float)rotationDgr, cX, cY);
        textureView.setTransform(mx);
    }

    /*-------------------------------------------------------------------------------------------------------------------------*/

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {

        if(requestCode == REQUEST_CODE_PERMISSIONS)
        {
            if(allPermissionsGranted())
            {
                startCamera();
            }
            else
            {
                Toast.makeText(this, "Permissions not granted by the user.", Toast.LENGTH_SHORT).show();
                finish();
            }
        }
    }

    /*-------------------------------------------------------------------------------------------------------------------------*/


}
