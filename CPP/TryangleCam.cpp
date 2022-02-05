#include <array>
#include <cstdio>
#include <gtk/gtk.h>
#include <iostream>
#include <memory>
#include <opencv2/highgui.hpp>
#include <opencv2/stitching.hpp>
#include <opencv2/video.hpp>
#include <stdexcept>
#include <string>
#include <vector>

using namespace cv;
using namespace std;

std::string exec(const char *cmd) {
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);

    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }

    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    return result;
}

int numDevices;

std::string deviceList;

std::vector<std::string> streamSources;

GtkApplication *app;

static void create_src_list(GtkWidget *widget, gpointer data) {
    std::cout << "secList\n";
    for (int i = 0; i < numDevices; i++) {
        streamSources.push_back(gtk_entry_get_text(GTK_ENTRY(((GtkWidget **)data)[i])));
    }
}

static void print_hello(GtkWidget *widget, gpointer data) {
    g_print("Hello World\n");
    GtkEntry *t = (GtkEntry *)data;
    std::string a = gtk_entry_get_text(GTK_ENTRY(t));
}

static void activate(GtkApplication *app, gpointer user_data) {
    GtkWidget *window;
    GtkWidget *button;
    GtkWidget *big_box;
    GtkWidget *label;
    GtkWidget *deviceListLabel;
    GtkWidget *tb;
    GtkWidget *logo;

    window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "Window");
    gtk_window_set_default_size(GTK_WINDOW(window), 200, 200);

    big_box = gtk_button_box_new(GTK_ORIENTATION_VERTICAL);
    gtk_container_add(GTK_CONTAINER(window), big_box);

    logo = gtk_image_new_from_file("tryanglecam.png");
    gtk_container_add(GTK_CONTAINER(big_box), logo);

    deviceListLabel = gtk_label_new(deviceList.c_str());
    gtk_container_add(GTK_CONTAINER(big_box), deviceListLabel);

    label = gtk_label_new("Enter space separated device names/url");
    gtk_container_add(GTK_CONTAINER(big_box), label);

    tb = gtk_entry_new();
    gtk_entry_set_placeholder_text(GTK_ENTRY(tb), "device name");
    gtk_container_add(GTK_CONTAINER(big_box), tb);

    button = gtk_button_new_with_label("Hello World");
    g_signal_connect(button, "clicked", G_CALLBACK(print_hello), tb);
    // g_signal_connect_swapped (button, "clicked", G_CALLBACK (gtk_widget_destroy), window);
    gtk_container_add(GTK_CONTAINER(big_box), button);

    gtk_widget_show_all(window);
}

void guiPart(int argc, char **argv) {
    int status;

    app = gtk_application_new("org.gtk.example", G_APPLICATION_FLAGS_NONE);
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
    status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);

    for (int i = 0; i < numDevices; i++) {
        std::cout << streamSources[i] << "\n";
    }
}

int main(int argc, char **argv) {
    std::cout << "Number of devices: ";
    std::cin >> numDevices;
    std::cout << numDevices << "\n";
    std::vector<std::string> devices;

    for (int i = 0; i < numDevices; i++) {
        std::cout << "Name of device: ";
        std::string s;
        std::cin >> s;
        devices.push_back(s);
    }

    // guiPart(argc, argv);

    std::cout << "Hi" << std::endl;

    // auto millisec_since_epoch = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    vector<cv::VideoCapture> streams;
    for (int i = 0; i < numDevices; i++) {
        streams.push_back(cv::VideoCapture(stoi(devices[i])));
    }

    // cv::VideoCapture rightStream(6);
    // cv::VideoCapture leftStream(2);
    // cv::VideoCapture midStream(4);

    // if(!leftStream.isOpened() || !rightStream.isOpened()){
    //     std::cout << "Error opening video stream or file\n";
    //     return -1;
    // }

    std::cout << "connected to streams" << std::endl;

    int cnt = 9;

    while (true) {
        vector<Mat> frames(numDevices);
        for (int i = 0; i < numDevices; i++) {
            streams[i] >> frames[i];
            cv::resize(frames[i], frames[i], cv::Size(), 0.5, 0.5);
        }

        // rightStream >> frames[0];
        // leftStream >> frames[2];
        // midStream >> frames[1];

        // cv::resize(frames[0], frames[0], cv::Size(), 0.5, 0.5);
        // cv::resize(frames[1], frames[1], cv::Size(), 0.5, 0.5);
        // cv::resize(frames[2], frames[2], cv::Size(), 0.5, 0.5);

        Mat pano;
        Ptr<Stitcher> stitcher = Stitcher::create(Stitcher::PANORAMA);
        Stitcher::Status status = stitcher->stitch(frames, pano);

        if (status != Stitcher::OK) {
            cout << "Can't stitch images, error code = " << int(status) << endl;
        } else {
            cout << "Got it!" << endl;
            cv::imshow("stitch", pano);
        }

        cv::imshow("right", frames[0]);
        if (numDevices > 1) {
            cv::imshow("mid", frames[1]);
        } else if (numDevices > 2) {
            cv::imshow("left", frames[2]);
        }

        char c = (char)cv::waitKey(25);
        if (c == 27) break;
    }
}
