#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "sensor_msgs/msg/joint_state.hpp"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <optional>
#include <string>

class DataAnalyzer : public rclcpp::Node
{
public:
    DataAnalyzer() : Node("data_analyzer"), wall_clock_(RCL_SYSTEM_TIME)
    {
        output_dir_ = this->declare_parameter<std::string>("output_dir", ".");
        std::filesystem::create_directories(output_dir_);

        cmd_file.open(output_dir_ + "/cmd_vel.csv");
        imu_file.open(output_dir_ + "/imu.csv");
        joint_file.open(output_dir_ + "/joint_states.csv");

        cmd_file << std::fixed << std::setprecision(6);
        imu_file << std::fixed << std::setprecision(6);
        joint_file << std::fixed << std::setprecision(6);

        cmd_file << "time,linear_x,angular_z\n";
        imu_file << "time,linear_acceleration_x,linear_acceleration_y,linear_acceleration_z\n";
        joint_file << "time,name,position,velocity,effort\n";
        
        sub_cmd_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10,
            std::bind(&DataAnalyzer::cmdCallback, this, std::placeholders::_1));

        sub_imu_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "/imu", 10,
            std::bind(&DataAnalyzer::imuCallback, this, std::placeholders::_1));

        sub_joint_ = this->create_subscription<sensor_msgs::msg::JointState>(
            "/joint_states", 10,
            std::bind(&DataAnalyzer::jointCallback, this, std::placeholders::_1));
    }

private:
    double stampToSeconds(const builtin_interfaces::msg::Time & stamp) const
    {
        return static_cast<double>(stamp.sec) + static_cast<double>(stamp.nanosec) * 1e-9;
    }

    bool hasStamp(const builtin_interfaces::msg::Time & stamp) const
    {
        return stamp.sec != 0 || stamp.nanosec != 0;
    }

    double relativeTime(double stamp_seconds, std::optional<double> & start_time)
    {
        if (!start_time) {
            start_time = stamp_seconds;
        }
        return stamp_seconds - *start_time;
    }

    double wallTimeSeconds() const
    {
        return wall_clock_.now().seconds();
    }

    void cmdCallback(const geometry_msgs::msg::Twist::SharedPtr msg)
    {
        const double t = relativeTime(wallTimeSeconds(), cmd_start_time_);
        cmd_file << t << "," << msg->linear.x << "," << msg->angular.z << "\n";
    }

    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg)
    {
        const double stamp = hasStamp(msg->header.stamp) ?
            stampToSeconds(msg->header.stamp) :
            wallTimeSeconds();
        const double t = relativeTime(stamp, imu_start_time_);
        imu_file << t << "," << msg->linear_acceleration.x << ","
                 << msg->linear_acceleration.y << ","
                 << msg->linear_acceleration.z << "\n";
    }

    void jointCallback(const sensor_msgs::msg::JointState::SharedPtr msg)
    {
        const double stamp = hasStamp(msg->header.stamp) ?
            stampToSeconds(msg->header.stamp) :
            wallTimeSeconds();

        const double t = relativeTime(stamp, joint_start_time_);

        for (size_t i = 0; i < msg->name.size(); i++)
        {
            const double position = i < msg->position.size() ? msg->position[i] : 0.0;
            const double velocity = i < msg->velocity.size() ? msg->velocity[i] : 0.0;
            const double effort = i < msg->effort.size() ? msg->effort[i] : 0.0;

            joint_file << t << ","
                    << msg->name[i] << ","
                    << position << ","
                    << velocity << ","
                    << effort << "\n";
        }
    }

    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr sub_cmd_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr sub_imu_;
    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr sub_joint_;

    std::ofstream cmd_file;
    std::ofstream imu_file;
    std::ofstream joint_file;
    std::string output_dir_;
    rclcpp::Clock wall_clock_;
    std::optional<double> cmd_start_time_;
    std::optional<double> imu_start_time_;
    std::optional<double> joint_start_time_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<DataAnalyzer>());
    rclcpp::shutdown();
    return 0;
}
