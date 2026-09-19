window.STUDY_V2 = {
zh:{
 flow:'共 40 组、160 项判断，预计约 20–30 分钟，实际用时因人而异。两个任务的先后顺序在参与者之间平衡分配；每组仅展示两个匿名方法。',
 promptNote:'',
 givenScope:'请评价生成的相机。人物动作已给定。',
 jointScope:'请分别评价生成的人物动作与相机。',
 criterionLabel:'评价维度',
 shortQuestions:{human_text:'人物 · 文本一致性',human_physics:'人物 · 动作自然度',camera_text:'相机 · 文本一致性',camera_geometry:'相机 · 运动合理性',framing:'相机 · 构图质量'},
 viewLabels:'上：Camera view（相机画面） · 下：Spatial view（空间视图）',
 transitionTitle:'第一阶段已完成，请休息片刻。',
 transitionText:'接下来进入另一种生成任务，请留意评估对象的变化。',
 continue:'开始下一阶段',
 tutorialTitle:'如何评价',
 tutorial:'观看两侧视频，逐项选择你的偏好。上方相机画面用于观察构图，下方空间视图用于观察人物动作与相机轨迹。“两者相当”表示表现接近；“无法判断”表示信息不足。点击评价维度可展开详细说明。',
 tutorialNext:'理解了，进入评估',
 testWelcome:'测试模式：本答卷不计入真人统计或正式配额。',
 buffering:'正在等待两侧视频缓冲…',
 questions:{
 human_text:['人物动作与文本的一致性','哪段人物动作更符合描述中的动作类型、身体部位与动作顺序？'],
 human_physics:['人物动作的自然与物理合理性','结合空间视图，哪段人物动作更自然、连贯，较少肢体扭曲、滑步或失衡？'],
 camera_text:['相机与文本的一致性','哪段相机运动更符合描述中的运动类型、方向与发生顺序？'],
 camera_geometry:['相机运动的平稳与空间合理性','结合空间视图，哪段相机位置与朝向变化更连贯、合理，较少突跳或抖动？'],
 framing:['相机画面的构图质量','哪段相机画面中的人物位置、大小、裁切与留白更恰当，且随时间更易于观看？']}
},
en:{
 flow:'40 comparisons and 160 judgments, approximately 20–30 minutes; actual completion time varies. Task order is counterbalanced across participants. Each trial shows two anonymous methods.',
 promptNote:'',
 givenScope:'Evaluate the generated camera. Human motion is supplied.',
 jointScope:'Evaluate generated human motion and camera separately.',
 criterionLabel:'Criterion',
 shortQuestions:{human_text:'Human · Text match',human_physics:'Human · Motion quality',camera_text:'Camera · Text match',camera_geometry:'Camera · Motion quality',framing:'Camera · Framing'},
 viewLabels:'Top: Camera view · Bottom: Spatial view',
 transitionTitle:'First part complete. Take a short break.',
 transitionText:'The next part evaluates the other generation task. Please note the change in what you are judging.',
 continue:'Begin next part',
 tutorialTitle:'How to evaluate',
 tutorial:'Watch both videos and select your preference for each criterion. Use the upper Camera view for framing and the lower Spatial view for human motion and camera trajectories. “About equal” means similar quality; “Cannot judge” means insufficient information. Click a criterion to expand its explanation.',
 tutorialNext:'Understood — begin evaluation',
 testWelcome:'Test mode: excluded from human results and formal assignment quotas.',
 buffering:'Waiting for both videos to buffer…',
 questions:{
 human_text:['Human–text alignment','Which human motion better matches the described action, body parts, and action order?'],
 human_physics:['Human motion quality','In the Spatial view, which human motion looks more natural and coherent, with fewer body distortions, foot-sliding artifacts, or balance problems?'],
 camera_text:['Camera–text alignment','Which camera movement better matches the described type, direction, and temporal order?'],
 camera_geometry:['Camera motion quality','In the Spatial view, which camera has more coherent and plausible position and orientation changes, with fewer jumps or jitters?'],
 framing:['Framing quality','Which camera view maintains more appropriate subject placement, size, cropping, and surrounding space over time?']}
}
};
