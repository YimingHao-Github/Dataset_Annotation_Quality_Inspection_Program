function main()
    % 设置目录路径（相对路径）
    data_dir = 'Data';
    label_dir = 'Label';
    merge_dir = 'Merge';

    % 加载所有标签
    label_dict = load_labels(label_dir);
    fprintf('已加载 %d 个标签文件\n', length(fieldnames(label_dict)));

    % 遍历Data目录，处理每张图片
    image_files = dir(fullfile(data_dir, '**', '*.png')); % 递归查找所有png文件
    for i = 1:length(image_files)
        image_path = fullfile(image_files(i).folder, image_files(i).name);
        fprintf('处理图片: %s\n', image_path);
        process_image(image_path, label_dict, merge_dir, label_dir);
    end

    fprintf('处理完成，所有图片已保存至Merge目录\n');
end

% 解析路径，提取视频编号、相机类型和帧编号
function [video_id, camera_type, frame_number] = parse_path(path)
    parts = split(path, filesep);
    video_id = parts{end-2}; % 倒数第三部分是视频编号
    camera_type = lower(parts{end-1}); % 倒数第二部分是相机类型，转为小写
    filename = parts{end}; % 最后一部分是文件名
    frame_parts = split(replace(filename, '.png', ''), '_');
    frame_number = frame_parts{end}; % 从文件名中提取帧编号
end

% 加载所有label文件到结构体中
function label_dict = load_labels(label_dir)
    label_dict = struct();
    txt_files = dir(fullfile(label_dir, '**', '*.txt')); % 递归查找所有txt文件

    for i = 1:length(txt_files)
        label_path = fullfile(txt_files(i).folder, txt_files(i).name);
        [video_id, camera_type, frame_number] = parse_path(label_path);
        key = sprintf('%s_%s_%s', video_id, camera_type, frame_number);

        % 读取标签文件
        try
            data = readmatrix(label_path, 'FileType', 'text', 'Delimiter', ' ');
            if size(data, 2) == 5 % YOLO标签应有5个值
                label_dict.(key) = data;
            else
                fprintf('警告: %s 中的标签格式错误\n', label_path);
            end
        catch e
            fprintf('警告: %s 中的标签格式错误: %s\n', label_path, e.message);
        end
    end
end

% 在图片上绘制标签
function image = draw_labels(image, labels)
    [h, w, ~] = size(image);

    for i = 1:size(labels, 1)
        label = labels(i, :);
        class_id = label(1);
        center_x = label(2);
        center_y = label(3);
        width = label(4);
        height = label(5);

        % 将归一化坐标转换为像素坐标
        x1 = floor((center_x - width/2) * w);
        y1 = floor((center_y - height/2) * h);
        x2 = floor((center_x + width/2) * w);
        y2 = floor((center_y + height/2) * h);

        % 绘制绿色边界框
        image = insertShape(image, 'Rectangle', [x1 y1 x2-x1 y2-y1], ...
            'LineWidth', 2, 'Color', 'green');
    end
end

% 处理单张图片
function process_image(image_path, label_dict, merge_dir, label_dir)
    [video_id, camera_type, frame_number] = parse_path(image_path);
    key = sprintf('%s_%s_%s', video_id, camera_type, frame_number);

    % 构建标签文件的路径
    label_filename = replace(extractAfter(image_path, filesep), '.png', '.txt');
    label_path = fullfile(label_dir, video_id, camera_type, label_filename);

    % 读取图片
    image = imread(image_path);
    if isempty(image)
        fprintf('错误: 无法读取图片 %s\n', image_path);
        return;
    end

    % 检查是否有标签
    if isfield(label_dict, key)
        labels = label_dict.(key);
        image = draw_labels(image, labels);
        fprintf('已绘制标签: %s\n', label_path);
    else
        fprintf('该图片没有标签文件: %s\n', image_path);
    end

    % 构造输出路径并保存
    output_dir = fullfile(merge_dir, video_id, camera_type);
    if ~exist(output_dir, 'dir')
        mkdir(output_dir);
    end
    output_path = fullfile(output_dir, extractAfter(image_path, filesep));
    imwrite(image, output_path);
end