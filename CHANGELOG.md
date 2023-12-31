# 更新日志

## [1.5.0] - 2023-

### 新增

* 新增了mcz文件识别功能。
* 向菜单栏中新增了导入mcz文件或歌曲文件夹的选项。
* 向菜单栏中新增了问题反馈的选项。

### 优化

* 优化了参数调节界面，实现了container内部自适应缩放。
* 将程序窗口初始大小从600×800更改为933×700。
* 现在将输出压缩文件到export文件夹。

### 变更

* 现在不需要将Malody谱面文件复制在程序同一目录下，而是通过导入谱面文件或谱面文件夹（遍历目录及子目录文件）的形式获取。

## [1.4.0] - 2023-07-20

### 新增

* 新增了Luck Mod和Flip Mod，其功能分别为打乱轨道顺序和左右翻转谱面，与Malody保持一致。
* 新增了曲绘作者作为可选输入项。

### 优化

* 现在BPM变化次数超过3次时，只显示持续小节数最长的BPM值与总BPM数。
* 优化了谱面相关信息的排版。

### 修复

* 修复了目录下存在".mcz"文件可能导致程序崩溃的问题。

### 变更

* 现在流速随BPM变化时以持续小节数最长的BPM值为基准进行调整，而非第一个BPM值。
* 现在使用CONST Mod选项作为BPM和effect对于流速改变控制的逻辑，而非分别控制流速是否随BPM变化、流速是否随effect变化，使之与Malody保持一致。
* 现在使用适配Ichzh3473模拟器的"info.csv"格式填写谱面元信息，而非Re:PhiEdit导出格式的"info.txt"。

## [1.3.0] - 2023-05-27

### 新增

* 现在可以正常适配使用"effect":"scroll"进行特效编写的谱面。

### 优化

* Phigros谱面写入speedEvent部分，使用双指针优化时间复杂度。
* 现在BPM变化次数超过5次时，减少显示个数。
* 减少基础流速默认值为13。

### 修复

* 修复了speedEvent终止时间错误的问题。
* 修复了windows窗口图标无法正常显示的问题。

## [1.2.2] - 2023-05-13

### 修复

* 修复了选择'流速随BPM变化'后切换谱面导致程序崩溃的问题。

## [1.2.1] - 2023-05-12

### 新增

* 新增5K~9K的轨道位置调整部分选项。

### 修复

* 修复部分数字输入框边界值、步进值错误的问题。

## [1.2.0] - 2023-05-07

### 变更

* 现在可以使用图形用户界面进行操作，而非命令提示符窗口。
* 现在程序的运行可以脱离Python运行环境。

## [1.1.0] - 2023-04-26

### 变更

* 现在可以脱离Python3编译器运行。

### 新增

* 现在可以自动将谱面所需的4个文件打包在'.zip'文件中。
* 增加流速随BPM变化的选项，即Malody中'CONST - 下落速度与BPM关联'模组关闭的状态。