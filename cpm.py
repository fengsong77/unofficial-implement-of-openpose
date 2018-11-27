import tensorflow as tf

class CpmStage1:
    def __init__(self, inputs_x, mask_cpm, mask_hm, gt_hm, gt_cpm, stage_num=6, hm_channel_num=19, cpm_channel_num=38):
        self.inputs_x = inputs_x
        self.mask_cpm = mask_cpm
        self.mask_hm = mask_hm
        self.gt_hm = gt_hm
        self.gt_cpm = gt_cpm
        self.stage_num = stage_num
        self.cpm_channel_num = cpm_channel_num
        self.hm_channel_num = hm_channel_num
        self.regularizer = tf.contrib.layers.l2_regularizer(scale=0.1)
    def add_layers(self, inputs):
        net = self.conv2(inputs=inputs, filters=256, padding='SAME', kernel_size=3)
        net = self.conv2(inputs=net, filters=128, padding='SAME', kernel_size=3)
        return net
    def stage_1(self, inputs, out_channel_num):
        # net = tf.layers.conv2d(inputs=inputs,
        #                        filters=128,
        #                        padding="same",
        #                        kernel_size=3,
        #                        activation="relu",
        #                        kernel_initializer=tf.random_normal_initializer(),
        #                        kernel_regularizer=self.regularizer)
        # # net = tf.layers.max_pooling2d(inputs=net, pool_size=2, strides=2)
        # net = tf.layers.conv2d(inputs=net,
        #                        filters=128,
        #                        padding="same",
        #                        kernel_size=3,
        #                        activation="relu",
        #                        kernel_initializer=tf.random_normal_initializer(),
        #                        kernel_regularizer=self.regularizer)
        # # net = tf.layers.max_pooling2d(inputs=net, pool_size=2, strides=2)
        # net = tf.layers.conv2d(inputs=net,
        #                        filters=128,
        #                        padding="same",
        #                        kernel_size=3,
        #                        activation="relu",
        #                        kernel_initializer=tf.random_normal_initializer(),
        #                        kernel_regularizer=self.regularizer)
        # # net = tf.layers.max_pooling2d(inputs=net, pool_size=2, strides=2)
        # net = tf.layers.conv2d(inputs=net,
        #                        filters=512,
        #                        padding="same",
        #                        kernel_size=1,
        #                        activation="relu",
        #                        kernel_initializer=tf.random_normal_initializer(),
        #                        kernel_regularizer=self.regularizer)
        # net = tf.layers.conv2d(inputs=net,
        #                        filters=out_channel_num,
        #                        padding="same",
        #                        kernel_size=1,
        #                        activation="relu",
        #                        kernel_initializer=tf.random_normal_initializer(),
        #                        kernel_regularizer=self.regularizer)
        net = self.conv2(inputs=inputs, filters=128, padding='SAME', kernel_size=3)
        net = self.conv2(inputs=net, filters=128, padding='SAME', kernel_size=3)
        net = self.conv2(inputs=net, filters=128, padding='SAME', kernel_size=3)
        net = self.conv2(inputs=net, filters=512, padding='SAME', kernel_size=1)
        net = self.conv2(inputs=net, filters=out_channel_num, padding='SAME', kernel_size=1)
        return net

    def stage_t(self, inputs, out_channel_num):
        net = tf.layers.conv2d(inputs=inputs,
                               filters=128,
                               padding="same",
                               kernel_size=7,
                               activation="relu",
                               bias_initializer=tf.random_normal_initializer(),
                               kernel_regularizer=self.regularizer)
        net = tf.layers.conv2d(inputs=net,
                               filters=128,
                               padding="same",
                               kernel_size=7,
                               activation="relu",
                               bias_initializer=tf.random_normal_initializer(),
                               kernel_regularizer=self.regularizer)
        net = tf.layers.conv2d(inputs=net,
                               filters=128,
                               padding="same",
                               kernel_size=7,
                               activation="relu",
                               bias_initializer=tf.random_normal_initializer(),
                               kernel_regularizer=self.regularizer)
        net = tf.layers.conv2d(inputs=net,
                               filters=128,
                               padding="same",
                               kernel_size=7,
                               activation="relu",
                               bias_initializer=tf.random_normal_initializer(),
                               kernel_regularizer=self.regularizer)
        net = tf.layers.conv2d(inputs=net,
                               filters=128,
                               padding="same",
                               kernel_size=7,
                               activation="relu",
                               bias_initializer=tf.random_normal_initializer(),
                               kernel_regularizer=self.regularizer)
        net = tf.layers.conv2d(inputs=net,
                               filters=128,
                               padding="same",
                               kernel_size=1,
                               activation="relu",
                               bias_initializer=tf.random_normal_initializer(),
                               kernel_regularizer=self.regularizer)
        net = tf.layers.conv2d(inputs=net,
                               filters=out_channel_num,
                               padding="same",
                               kernel_size=1,
                               activation="relu",
                               bias_initializer=tf.random_normal_initializer(),
                               kernel_regularizer=self.regularizer)
        return net

    def conv2(self, inputs, filters, padding, kernel_size):
        channels_in = inputs[0, 0, 0, :].get_shape().as_list()[0]
        with tf.name_scope('conv2d'):
            W = tf.Variable(tf.truncated_normal(
                [kernel_size, kernel_size, channels_in, filters], stddev=0.1), name='W')
            b = tf.Variable(tf.constant(0.1, shape=[filters]), name='b')
            conv = tf.nn.conv2d(inputs, W, strides=[1, 1, 1, 1], padding=padding)
            act = tf.nn.relu(conv + b)
        tf.summary.histogram('weights', W)
        tf.summary.histogram('biases', b)
        tf.summary.histogram('activations', act)
        return act

    def gen_net(self):
        cpm_loss = []
        hm_loss = []
        cpm_pre = []
        hm_pre = []
        with tf.variable_scope('add_layers'):
            added_layers_out = self.add_layers(inputs=self.inputs_x)

        with tf.variable_scope('stage1'):
            cpm_net = self.stage_1(inputs=added_layers_out, out_channel_num=self.cpm_channel_num)
            hm_net = self.stage_1(inputs=added_layers_out, out_channel_num=self.hm_channel_num)
            cpm_pre.append(cpm_net)
            hm_pre.append(hm_net)
            cpm_loss.append(self.get_loss(cpm_net, self.gt_cpm, mask_type='cpm'))
            hm_loss.append(self.get_loss(hm_net, self.gt_hm, mask_type='hm'))
            net = tf.concat([hm_net, cpm_net, added_layers_out], 3)

        with tf.variable_scope('staget'):
            for i in range(self.stage_num - 1):
                hm_net = self.stage_t(inputs=net, out_channel_num=self.hm_channel_num)
                cpm_net = self.stage_t(inputs=net, out_channel_num=self.cpm_channel_num)
                cpm_pre.append(cpm_net)
                hm_pre.append(hm_net)
                hm_loss.append(self.get_loss(hm_net, self.gt_hm, mask_type='hm'))
                cpm_loss.append(self.get_loss(cpm_net, self.gt_cpm, mask_type='cpm'))
                if i < self.stage_num - 2:
                    net = tf.concat([hm_net, cpm_net, added_layers_out], 3)

        with tf.name_scope("loss"):
            total_loss = tf.reduce_sum(hm_loss) + tf.reduce_sum(cpm_loss)
        tf.summary.scalar("loss", total_loss)

        # tf.summary.image('hm', self.gt_hm[:, :, :, 0:1], max_outputs=4)
        # tf.summary.image('hm_pre', hm_net[:, :, :, 0:1], max_outputs=4)

        return hm_pre, cpm_pre, total_loss


    # test code
    # def gen_net(self):
    #     cpm_loss = []
    #     hm_loss = []
    #     cpm_pre = []
    #     hm_pre = []
    #
    #     with tf.variable_scope('stage1'):
    #         with tf.name_scope('stage1'):
    #             cpm_net = self.stage_1(inputs=self.inputs_x, out_channel_num=self.cpm_channel_num)
    #             hm_net = self.stage_1(inputs=self.inputs_x, out_channel_num=self.hm_channel_num)
    #             cpm_pre.append(cpm_net)
    #             hm_pre.append(hm_net)
    #             cpm_loss.append(self.get_loss(cpm_net, self.gt_cpm, mask_type='cpm'))
    #             hm_loss.append(self.get_loss(hm_net, self.gt_hm, mask_type='hm'))
    #             net = tf.concat([hm_net, cpm_net, self.inputs_x], 3)
    #
    #     with tf.variable_scope('staget'):
    #         for i in range(self.stage_num - 1):
    #             with tf.name_scope("staget"):
    #                 hm_net = self.stage_t(inputs=net, out_channel_num=self.hm_channel_num)
    #                 cpm_net = self.stage_t(inputs=net, out_channel_num=self.cpm_channel_num)
    #                 cpm_pre.append(cpm_net)
    #                 hm_pre.append(hm_net)
    #                 hm_loss.append(self.get_loss(hm_net, self.gt_hm, mask_type='hm'))
    #                 cpm_loss.append(self.get_loss(cpm_net, self.gt_cpm, mask_type='cpm'))
    #                 if i < self.stage_num - 2:
    #                     net = tf.concat([hm_net, cpm_net, self.inputs_x], 3)
    #
    #     with tf.name_scope("loss"):
    #         total_loss = tf.reduce_sum(hm_loss) + tf.reduce_sum(cpm_loss)
    #     tf.summary.scalar("loss", total_loss)
    #
    #     tf.summary.image('hm', self.gt_hm[:, :, :, 0:1], max_outputs=4)
    #     tf.summary.image('hm_pre', hm_net[:, :, :, 0:1], max_outputs=4)
    #
    #     return hm_pre, cpm_pre, total_loss

    def get_loss(self, pre_y, gt_y, mask_type):
        if mask_type == 'cpm':
            return tf.reduce_mean(tf.reduce_sum(tf.square(gt_y - pre_y) * self.mask_cpm, axis=[1, 2, 3]))
        if mask_type == 'hm':
            return tf.reduce_mean(tf.reduce_sum(tf.square(gt_y - pre_y) * self.mask_hm, axis=[1, 2, 3]))
