# TinText子线程退出机制

`TinEngine.TinText`需要处理多线程渲染情况，由于处在子线程渲染时，渲染队列的添加是动态的，因此设置一个专门的内部函数来主动管理渲染队列的连续渲染比较麻烦，而在渲染方法结束后在这个线程内调用自身，会将子线程栈拓得较深，同时这样的结构也不符合`TinText`的模块单体化设计哲学。

`TinText`采用了事件绑定的子线程退出机制，即通过线程渲染结束后抛出窗口事件，触发主线程里的函数来进行下一次子线程中的渲染。这样做可以分开每次渲染的逻辑操作，同时确保上下文的无成本连贯。

> 线程成本由python本身的设计承担。

具体来说，就是`TinText`绑定了`<<CompleteRender>>`事件，在子线程渲染结束后，由渲染线程触发该事件，此时子线程结束。事件触发后，由`TinText`内部（处在主线程中）的函数内进行下一个渲染线程的创建和启动。