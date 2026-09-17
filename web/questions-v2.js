window.STUDY_V2 = {
zh:{
 flow:'共 40 组、160 项判断，预计约 20–30 分钟，实际用时因人而异。两个任务的先后顺序在参与者之间平衡分配；每组仅展示两个匿名方法。',
 promptNote:'只评价可见动作与镜头，不评价未渲染的服饰、道具或环境。人物在画面中变大或变小，不能单独说明相机前进或后退。中文译文有歧义时以英文原文为准。',
 viewLabels:'上：Camera view（相机画面） · 下：Spatial view（空间视图）',
 transitionTitle:'第一阶段已完成，请休息片刻。',
 transitionText:'接下来进入另一种生成任务，请留意评估对象的变化。',
 continue:'开始下一阶段',
 tutorialTitle:'正式作答前：两点练习',
 tutorial:'① 运动归因：人物向你走近、画面中的人物变大，并不代表相机一定前进。请结合空间视图判断相机位移。Truck 是平移，Pan 是转向；Boom 是升降，Tilt 是俯仰。② 两者相当表示能够比较且接近（也可能都差）；无法判断表示可见信息或理解不足。各题独立判断，语义更好不代表构图也更好。空间平台仅用于展示，不作为真实障碍物。',
 tutorialNext:'理解了，进入评估',
 testWelcome:'测试模式：本答卷不计入真人统计或正式配额。',
 buffering:'正在等待两侧视频缓冲…',
 questions:{
 human_text:['人物动作与文本的一致性','哪段人物动作更符合描述中的动作类型、身体部位与动作顺序？只判断可见的身体运动。'],
 human_physics:['人物动作的自然与物理合理性','哪段人物动作更自然、连贯，较少明显的肢体扭曲、滑步或不合理失衡？请看空间视图，不因相机裁切判人物更差。'],
 camera_text:['相机与文本的一致性','哪段相机运动更符合描述中的运动类型、方向与发生顺序？幅度更大本身不代表更符合。'],
 camera_geometry:['相机运动的平稳与空间合理性','哪段相机位置与朝向变化更连贯，较少非预期突跳、抖动或明显不合理的空间运动？请结合空间视图；静止或幅度较小本身不代表更好。'],
 framing:['相机画面的构图质量','哪段画面中人物的位置、大小、裁切与留白更恰当，且随时间更易于观看？请看相机画面；合理近景不要求全身入镜。']}
},
en:{
 flow:'40 comparisons and 160 judgments, approximately 20–30 minutes; actual completion time varies. Task order is counterbalanced across participants. Each trial shows two anonymous methods.',
 promptNote:'Judge visible motion and camera behavior, not unrendered clothing, objects, or environments. A change in the person’s image size alone does not determine the camera’s movement direction.',
 viewLabels:'Top: Camera view · Bottom: Spatial view',
 transitionTitle:'First part complete. Take a short break.',
 transitionText:'The next part evaluates the other generation task. Please note the change in what you are judging.',
 continue:'Begin next part',
 tutorialTitle:'Before answering: two practice concepts',
 tutorial:'1. Motion attribution: a person walking toward you and appearing larger does not imply that the camera moves forward. Use the Spatial view. Truck is translation, Pan is turning; Boom is vertical translation, Tilt is pitching. 2. About equal means the results are comparable and similar (possibly both poor). Unable to judge means the visible information or your understanding is insufficient. Judge each criterion separately. The display platform is not a real obstacle.',
 tutorialNext:'Understood — begin evaluation',
 testWelcome:'Test mode: excluded from human results and formal assignment quotas.',
 buffering:'Waiting for both videos to buffer…',
 questions:{
 human_text:['Human–text alignment','Which human motion better matches the described action, body parts, and action order? Judge only visible body motion.'],
 human_physics:['Human motion quality','Which human motion looks more natural and coherent, with fewer obvious body distortions, foot-sliding artifacts, or implausible balance changes? Use the Spatial view; do not penalize human motion for camera cropping.'],
 camera_text:['Camera–text alignment','Which camera motion better matches the described movement type, direction, and temporal order? Larger movement alone does not imply a better match.'],
 camera_geometry:['Camera motion quality','Which camera has more coherent position and orientation changes, with fewer unintended jumps, jitters, or visibly implausible spatial movements? Use the Spatial view; being static or moving less is not inherently better.'],
 framing:['Framing quality','Which camera view maintains more appropriate subject placement, size, cropping, and surrounding space over time? Use the Camera view; a suitable close-up need not show the full body.']}
}
};
